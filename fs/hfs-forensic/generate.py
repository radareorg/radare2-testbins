#!/usr/bin/env python3
"""Generate deterministic classic HFS recovery fixtures without platform tools."""
import gzip
import json
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
NODE = 512


def put(data, offset, fmt, *values):
    struct.pack_into('>' + fmt, data, offset, *values)


def extents(runs):
    return b''.join(struct.pack('>HH', start, count) for start, count in runs).ljust(12, b'\0')


def key(parent, name):
    name = name.encode('mac_roman')
    result = struct.pack('>BBIB', 6 + len(name), 0, parent, len(name)) + name
    return result + bytes(len(result) % 2)


def record(parent, name, cnid, block, size=0, runs=(), physical=None, resource=b'', directory=False):
    value = bytearray(70 if directory else 102)
    value[0] = 1 if directory else 2
    put(value, 6 if directory else 20, 'I', cnid)
    if not directory:
        put(value, 26, 'II', size, block * (sum(count for _, count in runs) if physical is None else physical))
        put(value, 36, 'II', len(resource), block if resource else 0)
        value[74:86] = extents(runs[:3])
        value[86:98] = extents([(90 if cnid == 20 else 114, 1)] if resource else [])
    return key(parent, name) + value


def thread(cnid, parent, name, directory=False):
    value = bytearray(46)
    value[0] = 3 if directory else 4
    put(value, 10, 'I', parent)
    name = name.encode('mac_roman')
    value[14] = len(name)
    value[15:15 + len(name)] = name
    return key(cnid, '') + value


def node(kind, height, records, next_=0, previous=0):
    result = bytearray(NODE)
    put(result, 0, 'IIbBHH', next_, previous, kind, height, len(records), 0)
    offset, locations = 14, []
    for index, item in enumerate(records):
        locations.append(offset)
        put(result, NODE - 2 * (index + 1), 'H', offset)
        result[offset:offset + len(item)] = item
        offset += len(item)
        assert not offset % 2
    assert offset <= NODE - 2 * (len(records) + 1)
    put(result, NODE - 2 * (len(records) + 1), 'H', offset)
    return result, locations, offset


def header(nodes, root, depth, count, first, last, allocated):
    value = bytearray(106)
    put(value, 0, 'HIIIIHHII', depth, root, count, first, last, NODE, 37, nodes, nodes - len(allocated))
    bitmap = bytearray(256)
    for bit in allocated:
        bitmap[bit // 8] |= 128 >> (bit % 8)
    return node(1, 0, [value, bytes(128), bitmap])[0]


def build(block):
    allocation, bitmap = 5 * 512, 3 * 512
    catalog, overflow = allocation + 12 * block, allocation + 4 * block
    image = bytearray(allocation + 128 * block + 1024)
    used = set(range(4, 4 + (3 * NODE + block - 1) // block))
    used.update(range(12, 12 + (7 * NODE + block - 1) // block))
    used.update([80, 81, 82, 84, 86, 88, 90, 92, 94, 96])
    mdb = bytearray(512)
    put(mdb, 0, 'H', 0x4244)
    put(mdb, 10, 'H', 1 << 8)
    put(mdb, 14, 'HHHIIH', 3, 0, 128, block, block, 5)
    put(mdb, 30, 'IH', 40, 128 - len(used))
    mdb[36:45] = b'\x08Forensic'
    put(mdb, 130, 'I', 3 * NODE)
    mdb[134:146] = extents([(4, (3 * NODE + block - 1) // block)])
    put(mdb, 146, 'I', 7 * NODE)
    mdb[150:162] = extents([(12, (7 * NODE + block - 1) // block)])
    image[1024:1536] = mdb
    image[-1024:-512] = mdb
    for bit in used:
        image[bitmap + bit // 8] |= 128 >> (bit % 8)

    def store_tree(base, index, data):
        image[base + index * NODE:base + (index + 1) * NODE] = data

    def overflow_record(cnid, start, runs):
        return struct.pack('>BBIH', 7, 0, cnid, start) + extents(runs)

    live_extents = [overflow_record(5, 0, [(94, 1)]), overflow_record(21, 3, [(88, 1)])]
    store_tree(overflow, 0, header(3, 1, 1, 2, 1, 1, [0, 1]))
    store_tree(overflow, 1, node(-1, 1, live_extents)[0])
    store_tree(overflow, 2, node(-1, 1, [overflow_record(30, 3, [(110, 1)])])[0])

    def file(parent, name, cnid, size=0, runs=(), **kwargs):
        return record(parent, name, cnid, block, size, runs, **kwargs)

    leaves = {
        2: [file(1, 'Forensic', 2, directory=True), thread(2, 1, 'Forensic', True),
            file(2, 'café', 22, 9, [(92, 1)])],
        3: [file(2, 'empty', 23),
            file(2, 'fragmented.bin', 21, 4 * block, [(82, 1), (84, 1), (86, 1)], physical=4)],
        6: [file(2, 'live.txt', 20, 14, [(80, 2)], resource=b'resource\n')],
    }
    store_tree(catalog, 0, header(7, 1, 2, 6, 2, 6, [0, 1, 2, 3, 6]))
    store_tree(catalog, 1, node(0, 2, [key(1, 'Forensic') + struct.pack('>I', 2),
                                     key(2, 'empty') + struct.pack('>I', 3),
                                     key(2, 'live.txt') + struct.pack('>I', 6)])[0])
    locations, slack = {}, []
    for index, records in leaves.items():
        data, offsets, end = node(-1, 1, records, {2: 3, 3: 6, 6: 0}[index], {2: 0, 3: 2, 6: 3}[index])
        if index == 2:
            locations['22'] = index * NODE + offsets[2]
        slack.append([index * NODE + end, NODE - 2 * (len(records) + 1) - end])
        if index == 6:
            locations['slack.txt'] = index * NODE + end
            item = file(2, 'slack.txt', 31, 23, [(116, 1)])
            data[end:end + len(item)] = item
        store_tree(catalog, index, data)

    deleted = [file(2, 'vanished.bin', 30, 3 * block + 17, [(104, 1), (106, 1), (108, 1)],
                    physical=4, resource=b'deleted resource\n'),
               file(2, 'gone', 32, directory=True), file(32, 'child.txt', 33, 6, [(118, 1)])]
    retained = [thread(34, 2, 'thread-only'), thread(35, 2, 'lost-dir', True),
                file(35, 'lost-child', 36, 11, [(120, 1)]), thread(30, 2, 'vanished.bin')]
    for index, records, names in ((4, deleted, ['vanished.bin', 'gone', 'child.txt']),
                                  (5, retained, ['thread-only', 'lost-dir', 'lost-child', 'name-thread'])):
        data, offsets, _ = node(-1, 1, records)
        locations.update({name: index * NODE + offset for name, offset in zip(names, offsets)})
        store_tree(catalog, index, data)

    contents = {80: b'Live HFS file\n' + b'L' * (block - 14), 81: b'S' * block,
                90: b'resource\n' + b'R' * (block - 9), 92: b'MacRoman\n', 96: b'orphan\n',
                100: b'FREE HFS', 114: b'deleted resource\n', 116: b'Catalog slack recovery\n',
                118: b'child\n', 120: b'lost child\n'}
    contents.update({start: bytes([letter]) * block for start, letter in
                     ((82, 65), (84, 66), (86, 67), (88, 68), (104, 68), (106, 69), (108, 70), (110, 71))})
    for start, content in contents.items():
        offset = allocation + start * block
        image[offset:offset + len(content)] = content
    ids = {name: (1 << 63) | locations[name] for name in
           ('vanished.bin', 'gone', 'child.txt', 'slack.txt', 'thread-only', 'lost-dir', 'lost-child')}
    return image, dict(block=block, allocation=allocation, bitmap=bitmap, catalog=catalog,
                       overflow=overflow, locations=locations, catalog_slack=slack, ids=ids)


if __name__ == '__main__':
    manifest = {}
    for name, block in [('hfs', 512), ('hfs-1536', 1536)]:
        image, manifest[name] = build(block)
        (HERE / (name + '.img.gz')).write_bytes(gzip.compress(image, mtime=0))
    (HERE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
