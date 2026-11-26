#!/usr/bin/env python3
"""Generate tiny classic HFS forensic fixtures using only Python's standard library."""
import gzip
import json
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
NODE = 512


def extents(values):
    return b''.join(struct.pack('>HH', *value) for value in values).ljust(12, b'\0')


def key(parent, name):
    name = name.encode('mac_roman')
    value = struct.pack('>BBIB', 6 + len(name), 0, parent, len(name)) + name
    return value + bytes(len(value) & 1)


def record(parent, name, cnid, data=(), size=0, resource=(), resource_size=0, directory=False, block=512):
    value = bytearray(70 if directory else 102)
    struct.pack_into('>H', value, 0, 0x100 if directory else 0x200)
    struct.pack_into('>I', value, 6 if directory else 20, cnid)
    struct.pack_into('>II', value, 10 if directory else 44, 2082844800 + 1700000000, 2082844800 + 1700000001)
    if not directory:
        struct.pack_into('>II', value, 26, size, sum(count for _, count in data) * block)
        struct.pack_into('>II', value, 36, resource_size, sum(count for _, count in resource) * block)
        value[74:86], value[86:98] = extents(data[:3]), extents(resource[:3])
    return key(parent, name) + value


def thread(cnid, parent, name, directory=False):
    value = bytearray(46)
    name = name.encode('mac_roman')
    struct.pack_into('>HI', value, 0, 0x300 if directory else 0x400, 0)
    struct.pack_into('>I', value, 10, parent)
    value[14] = len(name)
    value[15:15 + len(name)] = name
    return key(cnid, '') + value


def node(kind, height, records, next_=0, previous=0):
    value = bytearray(NODE)
    struct.pack_into('>IIbBHH', value, 0, next_, previous, kind, height, len(records), 0)
    offset, locations = 14, []
    for index, record_ in enumerate(records):
        locations.append(offset)
        struct.pack_into('>H', value, NODE - (index + 1) * 2, offset)
        value[offset:offset + len(record_)] = record_
        offset = (offset + len(record_) + 1) & ~1
    assert offset <= NODE - (len(records) + 1) * 2
    struct.pack_into('>H', value, NODE - (len(records) + 1) * 2, offset)
    return value, locations, offset


def header(nodes, root, depth, records, first, last, allocated, key_size):
    value = bytearray(106)
    struct.pack_into('>HIIIIHHII', value, 0, depth, root, records, first, last, NODE, key_size,
                     nodes, nodes - len(allocated))
    bitmap = bytearray(256)
    for bit in allocated:
        bitmap[bit // 8] |= 128 >> (bit % 8)
    return node(1, 0, [value, bytes(128), bitmap])[0]


def build(block):
    allocation = 5 * 512
    image = bytearray(allocation + 128 * block + 1024)
    catalog, overflow = allocation + 12 * block, allocation + 4 * block
    bitmap = 3 * 512
    used = set(range(4, 4 + (3 * NODE + block - 1) // block))
    used.update(range(12, 12 + (8 * NODE + block - 1) // block))
    used.update((80, 81, 82, 84, 86, 88, 90, 92, 94, 96))
    metadata = bytearray(512)
    struct.pack_into('>H', metadata, 0, 0x4244)
    struct.pack_into('>HHHH', metadata, 10, 1 << 8, 0, 3, 0)
    struct.pack_into('>HIIH', metadata, 18, 128, block, block, 5)
    struct.pack_into('>IH', metadata, 30, 40, 128 - len(used))
    metadata[36:45] = b'\x08Forensic'
    struct.pack_into('>I', metadata, 130, 3 * NODE)
    metadata[134:146] = extents([(4, (3 * NODE + block - 1) // block)])
    struct.pack_into('>I', metadata, 146, 8 * NODE)
    metadata[150:162] = extents([(12, (8 * NODE + block - 1) // block)])
    image[1024:1536] = metadata
    image[-1024:-512] = metadata
    for bit in used:
        image[bitmap + bit // 8] |= 128 >> (bit % 8)

    def file(parent, name, cnid, data=(), size=0, resource=(), resource_size=0, directory=False):
        return record(parent, name, cnid, data, size, resource, resource_size, directory, block)

    live = [file(1, 'Forensic', 2, directory=True), thread(2, 1, 'Forensic', True),
            file(2, 'live.txt', 20, [(80, 2)], len(b'Live HFS file\n'), [(90, 1)], len(b'resource\n')),
            file(2, 'fragmented.bin', 21, [(82, 1), (84, 1), (86, 1), (88, 1)], 4 * block),
            file(2, 'café', 22, [(92, 1)], len(b'MacRoman\n')), file(2, 'empty', 23)]
    live.sort(key=lambda value: (struct.unpack_from('>I', value, 2)[0],
                                 value[7:7 + value[6]].decode('mac_roman').lower()))
    chunks, chunk = [], []
    for value in live:
        if 14 + sum(len(item) for item in chunk + [value]) + 2 * (len(chunk) + 2) > NODE - 150:
            chunks.append(chunk)
            chunk = []
        chunk.append(value)
    chunks.append(chunk)
    assert len(chunks) == 3
    leaf_ids = [2, 3, 6]
    image[catalog:catalog + NODE] = header(8, 1, 2, len(live), 2, 6, [0, 1] + leaf_ids, 37)
    index = [key(struct.unpack_from('>I', chunk[0], 2)[0], chunk[0][7:7 + chunk[0][6]].decode('mac_roman')) + struct.pack('>I', number)
             for number, chunk in zip(leaf_ids, chunks)]
    image[catalog + NODE:catalog + 2 * NODE] = node(0, 2, index)[0]
    locations, slack_locations = {}, []
    for order, (number, chunk) in enumerate(zip(leaf_ids, chunks)):
        value, offsets, end = node(-1, 1, chunk, leaf_ids[order + 1] if order < 2 else 0,
                                    leaf_ids[order - 1] if order else 0)
        slack_locations.append((number * NODE + end, NODE - (len(chunk) + 1) * 2 - end))
        if order == 2:
            retained = file(2, 'slack.txt', 31, [(116, 1)], len(b'Catalog slack recovery\n'))
            assert len(retained) <= slack_locations[-1][1]
            value[end:end + len(retained)] = retained
            locations['slack.txt'] = number * NODE + end
        image[catalog + number * NODE:catalog + (number + 1) * NODE] = value
        for raw, offset in zip(chunk, offsets):
            start = (raw[0] + 2) & ~1
            if raw[start] in (1, 2):
                cnid = struct.unpack_from('>I', raw, start + (6 if raw[start] == 1 else 20))[0]
                locations[str(cnid)] = number * NODE + offset

    retained = [file(2, 'vanished.bin', 30, [(104, 1), (106, 1), (108, 1), (110, 1)], 3 * block + 17,
                     [(114, 1)], len(b'deleted resource\n')),
                file(2, 'gone', 32, directory=True), file(32, 'child.txt', 33, [(118, 1)], 6)]
    value, offsets, _ = node(-1, 1, retained)
    image[catalog + 4 * NODE:catalog + 5 * NODE] = value
    for name, offset in zip(('vanished.bin', 'gone', 'child.txt'), offsets):
        locations[name] = 4 * NODE + offset
    retained = [thread(34, 2, 'thread-only'), thread(35, 2, 'lost-dir', True),
                file(35, 'lost-child', 36, [(120, 1)], len(b'lost child\n')), thread(30, 2, 'vanished.bin')]
    value, offsets, _ = node(-1, 1, retained)
    image[catalog + 5 * NODE:catalog + 6 * NODE] = value
    for name, offset in zip(('thread-only', 'lost-dir', 'lost-child', 'name-thread'), offsets):
        locations[name] = 5 * NODE + offset

    def overflow_record(cnid, start, extent):
        return struct.pack('>BBIH', 7, 0, cnid, start) + extents([extent])

    records = [overflow_record(5, 0, (94, 1)), overflow_record(21, 3, (88, 1))]
    image[overflow:overflow + NODE] = header(3, 1, 1, 2, 1, 1, [0, 1], 7)
    image[overflow + NODE:overflow + 2 * NODE] = node(-1, 1, records)[0]
    image[overflow + 2 * NODE:overflow + 3 * NODE] = node(-1, 1, [overflow_record(30, 3, (110, 1))])[0]
    for number, byte in ((80, b'L'), (81, b'S'), (90, b'R'), (104, b'D'), (106, b'E'), (108, b'F'), (110, b'G')):
        start = allocation + number * block
        image[start:start + block] = byte * block
    for number, payload in ((80, b'Live HFS file\n'), (90, b'resource\n'), (92, b'MacRoman\n'),
                            (96, b'orphan\n'), (100, b'FREE HFS EVIDENCE\n'),
                            (114, b'deleted resource\n'), (118, b'child\n'), (120, b'lost child\n'),
                            (116, b'Catalog slack recovery\n')):
        start = allocation + number * block
        image[start:start + len(payload)] = payload
    for number, byte in zip((82, 84, 86, 88), b'ABCD'):
        image[allocation + number * block:allocation + (number + 1) * block] = bytes([byte]) * block
    ids = {name: (1 << 63) | offset for name, offset in locations.items() if not name.isdecimal()}
    return image, dict(block=block, allocation=allocation, bitmap=bitmap, catalog=catalog, overflow=overflow,
                       locations=locations, ids=ids, catalog_slack=slack_locations, leaf_ids=leaf_ids)


def main():
    manifest = {}
    for name, block in (('hfs', 512), ('hfs-1536', 1536)):
        image, info = build(block)
        compressed = gzip.compress(image, mtime=0)
        (HERE / (name + '.img.gz')).write_bytes(compressed)
        manifest[name] = info
        print(name, len(image), len(compressed), 'compressed bytes')
    (HERE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
