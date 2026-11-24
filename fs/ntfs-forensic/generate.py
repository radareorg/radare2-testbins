#!/usr/bin/env python3
"""Create a compact NTFS image with retained deleted MFT data and explicit run maps."""
import gzip
import json
from pathlib import Path
import struct
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent


def u16(data, offset):
    return struct.unpack_from('<H', data, offset)[0]


def u32(data, offset):
    return struct.unpack_from('<I', data, offset)[0]


def u64(data, offset):
    return struct.unpack_from('<Q', data, offset)[0]


def aligned(value):
    return (value + 7) & ~7


def decode_runs(attr, cluster):
    vcn, lcn, offset = u64(attr, 16), 0, u16(attr, 32)
    result = []
    while attr[offset]:
        lengths = attr[offset]
        offset += 1
        count_size, delta_size = lengths & 15, lengths >> 4
        count = int.from_bytes(attr[offset:offset + count_size], 'little')
        offset += count_size
        if delta_size:
            lcn += int.from_bytes(attr[offset:offset + delta_size], 'little', signed=True)
        offset += delta_size
        result.append((vcn * cluster, lcn * cluster if delta_size else None, count * cluster))
        vcn += count
    return result


def mapping_pairs(runs):
    previous, result = 0, bytearray()
    for count, lcn in runs:
        count_size = max(1, (count.bit_length() + 7) // 8)
        delta_size = 0
        delta = b''
        if lcn is not None:
            difference = lcn - previous
            delta_size = next(size for size in range(1, 9) if -(1 << (size * 8 - 1)) <= difference < (1 << (size * 8 - 1)))
            delta = difference.to_bytes(delta_size, 'little', signed=True)
            previous = lcn
        result.append((delta_size << 4) | count_size)
        result.extend(count.to_bytes(count_size, 'little'))
        result.extend(delta)
    return result + bytes(1)


with tempfile.TemporaryDirectory(prefix='ntfs-forensic-') as directory:
    temporary = Path(directory)
    disk = temporary / 'recovery.img'
    disk.write_bytes(bytes(8 * 1024 * 1024))
    subprocess.run(['mkntfs', '-F', '-Q', '-q', '-T', '-s', '512', '-c', '512', str(disk)], check=True, capture_output=True)
    contents = {
        'live.txt': b'Live NTFS file\n',
        'vanished.bin': b'Recover NTFS data\n' * 1024,
        'inline.txt': b'Resident NTFS recovery\n' * 16,
        'sparse.bin': b'A' * 512 + b'Z' * 512 + bytes(3072),
        'unwritten.bin': b'Initialized NTFS\n' + b'X' * (1024 - 17),
    }
    for name, data in contents.items():
        source = temporary / name
        source.write_bytes(data)
        subprocess.run(['ntfscp', '-f', str(disk), str(source), '/' + name], check=True, capture_output=True)
    image = bytearray(disk.read_bytes())
    sector = u16(image, 11)
    cluster = sector * image[13]
    encoded = struct.unpack_from('<b', image, 64)[0]
    record_size = encoded * cluster if encoded > 0 else 1 << -encoded
    mft_start = u64(image, 48) * cluster

    def unfix(data):
        data = bytearray(data)
        usa, count = u16(data, 4), u16(data, 6)
        for index in range(1, count):
            assert data[index * sector - 2:index * sector] == data[usa:usa + 2]
            data[index * sector - 2:index * sector] = data[usa + index * 2:usa + index * 2 + 2]
        return data

    def attributes(record):
        offset = u16(record, 20)
        while u32(record, offset) != 0xffffffff:
            length = u32(record, offset + 4)
            yield offset, record[offset:offset + length]
            offset += length

    zero = unfix(image[mft_start:mft_start + record_size])
    mft_attr = next(attr for offset, attr in attributes(zero) if u32(attr, 0) == 0x80 and not attr[9])
    mft_runs = decode_runs(mft_attr, cluster)
    count = u64(mft_attr, 56) // record_size

    def record_location(number):
        logical = number * record_size
        for start, physical, size in mft_runs:
            if start <= logical < start + size:
                assert physical is not None and record_size <= start + size - logical
                return physical + logical - start
        raise AssertionError(number)

    def record(number):
        offset = record_location(number)
        return unfix(image[offset:offset + record_size])

    def store_record(number, data):
        data = bytearray(data)
        usa, entries = u16(data, 4), u16(data, 6)
        for index in range(1, entries):
            data[usa + index * 2:usa + index * 2 + 2] = data[index * sector - 2:index * sector]
            data[index * sector - 2:index * sector] = data[usa:usa + 2]
        offset = record_location(number)
        image[offset:offset + record_size] = data

    def replace_attribute(data, offset, value):
        old_size, used = u32(data, offset + 4), u32(data, 24)
        tail = bytes(data[offset + old_size:used])
        new_used = offset + len(value) + len(tail)
        assert new_used <= record_size
        data[offset:new_used] = value + tail
        data[new_used:] = bytes(record_size - new_used)
        struct.pack_into('<I', data, 24, new_used)

    ids = {}
    for number in range(count):
        try:
            data = record(number)
        except AssertionError:
            continue
        for offset, attr in attributes(data):
            if u32(attr, 0) == 0x30 and not attr[8]:
                value = attr[u16(attr, 20):]
                if len(value) >= 66:
                    name = value[66:66 + value[64] * 2].decode('utf-16le')
                    if name in contents:
                        ids[name] = number
    assert set(ids) == set(contents), ids

    def set_bit(stream_record, attr_type, index, allocated):
        data = record(stream_record)
        offset, attr = next((offset, attr) for offset, attr in attributes(data) if u32(attr, 0) == attr_type and not attr[9])
        if attr[8]:
            runs = decode_runs(attr, cluster)
            logical = index // 8
            start, physical, size = next(run for run in runs if run[0] <= logical < run[0] + run[2])
            address = physical + logical - start
            image[address] = (image[address] | (1 << (index % 8))) if allocated else (image[address] & ~(1 << (index % 8)))
        else:
            byte = offset + u16(attr, 20) + index // 8
            data[byte] = (data[byte] | (1 << (index % 8))) if allocated else (data[byte] & ~(1 << (index % 8)))
            store_record(stream_record, data)

    number = ids['vanished.bin']
    data = record(number)
    offset, attr = next((offset, attr) for offset, attr in attributes(data) if u32(attr, 0) == 0x80 and not attr[9])
    original_runs = decode_runs(attr, cluster)
    assert len(original_runs) == 1
    first = original_runs[0][1] // cluster
    clusters = original_runs[0][2] // cluster
    assert clusters == (len(contents['vanished.bin']) + cluster - 1) // cluster, clusters
    split = clusters // 3
    runs = [(split, first), (clusters - split * 2, first + split * 2), (split, first + split)]
    logical = 0
    for length, physical in runs:
        payload = contents['vanished.bin'][logical:logical + length * cluster]
        image[physical * cluster:physical * cluster + len(payload)] = payload
        logical += len(payload)
    encoded_runs = mapping_pairs(runs)
    value = bytearray(attr[:64]) + encoded_runs
    value.extend(bytes(aligned(len(value)) - len(value)))
    struct.pack_into('<I', value, 4, len(value))
    replace_attribute(data, offset, value)
    struct.pack_into('<H', data, 22, u16(data, 22) & ~1)
    store_record(number, data)
    set_bit(0, 0xb0, number, False)
    for index in range(first, first + clusters):
        set_bit(6, 0x80, index, False)

    inline = ids['inline.txt']
    data = record(inline)
    struct.pack_into('<H', data, 22, u16(data, 22) & ~1)
    store_record(inline, data)
    set_bit(0, 0xb0, inline, False)

    sparse = ids['sparse.bin']
    data = record(sparse)
    offset, attr = next((offset, attr) for offset, attr in attributes(data) if u32(attr, 0) == 0x80 and not attr[9])
    old_runs = decode_runs(attr, cluster)
    assert len(old_runs) == 1 and not attr[8] == 0
    first_sparse = old_runs[0][1] // cluster
    holes = (1 << 32) // cluster - 1
    sparse_runs = [(1, first_sparse), (holes, None), (1, first_sparse + 1)]
    value = bytearray(attr[:64]) + struct.pack('<Q', 2 * cluster) + mapping_pairs(sparse_runs)
    value.extend(bytes(aligned(len(value)) - len(value)))
    struct.pack_into('<I', value, 4, len(value))
    struct.pack_into('<H', value, 12, 0x8000)
    struct.pack_into('<Q', value, 24, holes + 1)
    struct.pack_into('<H', value, 32, 72)
    struct.pack_into('<QQQ', value, 40, 2 * cluster, (1 << 32) + cluster, (1 << 32) + cluster)
    replace_attribute(data, offset, value)
    store_record(sparse, data)
    for index in range(first_sparse + 2, (old_runs[0][1] + old_runs[0][2]) // cluster):
        set_bit(6, 0x80, index, False)

    unwritten = ids['unwritten.bin']
    data = record(unwritten)
    offset, attr = next((offset, attr) for offset, attr in attributes(data) if u32(attr, 0) == 0x80 and not attr[9])
    assert attr[8]
    struct.pack_into('<Q', data, offset + 56, 17)
    store_record(unwritten, data)

    (HERE / 'recovery.img.gz').write_bytes(gzip.compress(image, mtime=0))
    manifest = {'ids': ids, 'sector': sector, 'cluster': cluster, 'record_size': record_size,
                'mft_runs': mft_runs, 'record_offsets': {str(number): record_location(number) for number in range(count)},
                'deleted_runs': runs, 'sparse_runs': sparse_runs, 'deleted_size': len(contents['vanished.bin'])}
    (HERE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(ids, len(gzip.compress(image, mtime=0)), 'compressed bytes')
