#!/usr/bin/env python3
"""Build compact, deterministic HFS+/HFSX forensic images without platform tools."""
import gzip
import json
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
NODE = 4096


def fork(size, extents, blocks=None):
    result = bytearray(80)
    struct.pack_into('>QII', result, 0, size, 0, sum(count for _, count in extents) if blocks is None else blocks)
    for index, (start, count) in enumerate(extents):
        struct.pack_into('>II', result, 16 + index * 8, start, count)
    return result


def key(parent, name):
    encoded = name.encode('utf-16be')
    return struct.pack('>HIH', 6 + len(encoded), parent, len(encoded) // 2) + encoded


def catalog_record(parent, name, cnid, data=None, resource=None, directory=False):
    value = bytearray(88 if directory else 248)
    struct.pack_into('>HHII', value, 0, 1 if directory else 2, 0, 0, cnid)
    struct.pack_into('>I', value, 16, 2082844800 + 1700000000)
    struct.pack_into('>H', value, 42, 0o40755 if directory else 0o100644)
    if not directory:
        value[88:168] = data or bytes(80)
        value[168:248] = resource or bytes(80)
    return key(parent, name) + value


def thread(cnid, parent, name, directory=False):
    encoded = name.encode('utf-16be')
    return key(cnid, '') + struct.pack('>HHIH', 3 if directory else 4, 0, parent, len(encoded) // 2) + encoded


def node(kind, height, records, next_=0, previous=0):
    result = bytearray(NODE)
    struct.pack_into('>IIbBHH', result, 0, next_, previous, kind, height, len(records), 0)
    offset = 14
    locations = []
    for index, record in enumerate(records):
        locations.append(offset)
        struct.pack_into('>H', result, NODE - (index + 1) * 2, offset)
        result[offset:offset + len(record)] = record
        offset += len(record)
        if offset & 1:
            offset += 1
    assert offset <= NODE - (len(records) + 1) * 2
    struct.pack_into('>H', result, NODE - (len(records) + 1) * 2, offset)
    return result, locations, offset


def tree_header(nodes, root, depth, records, first, last, allocated, compare=0xcf):
    header = bytearray(106)
    struct.pack_into('>HIIIIHHII', header, 0, depth, root, records, first, last, NODE, 516, nodes, nodes - len(allocated))
    header[37] = compare
    struct.pack_into('>I', header, 38, 2)
    bitmap = bytearray(NODE - 14 - 106 - 128 - 8)
    for bit in allocated:
        bitmap[bit // 8] |= 128 >> (bit % 8)
    return node(1, 0, [header, bytes(128), bitmap])[0]


def checksum(data):
    value = 0
    for byte in data:
        value = ((value << 8) ^ (value + byte)) & 0xffffffff
    return (~value) & 0xffffffff


def build(block=512, sensitive=False):
    image = bytearray(256 * block)
    used = set(range((1536 + block - 1) // block)) | {255, (len(image) - 1024) // block}
    used |= {3, 68, 69, 70, 71, 72, 73, 80, 120, 122, 124, 126}
    for start, nodes in ((4, 2), (20, 4), (52, 2)):
        used.update(range(start, start + nodes * NODE // block))
    fragments = [82 + index * 2 for index in range(9)]
    used.update(fragments)
    header = bytearray(512)
    struct.pack_into('>HHIII', header, 0, 0x4858 if sensitive else 0x482b, 5 if sensitive else 4,
                     (1 << 8) | (1 << 9) | (1 << 13), 0x4831302b, 69)
    struct.pack_into('>II', header, 32, 2, 1)
    struct.pack_into('>II', header, 40, block, 256)
    struct.pack_into('>I', header, 48, 256 - len(used))
    struct.pack_into('>I', header, 64, 40)
    header[112:192] = fork(32, [(3, 1)])
    header[192:272] = fork(2 * NODE, [(4, 2 * NODE // block)])
    header[272:352] = fork(4 * NODE, [(20, 4 * NODE // block)])
    header[352:432] = fork(2 * NODE, [(52, 2 * NODE // block)])
    header[432:512] = fork(block, [(68, 1)])
    image[1024:1536] = header
    image[-1024:-512] = header
    for bit in used:
        image[3 * block + bit // 8] |= 128 >> (bit % 8)

    extents = []
    for cnid, start, mappings in ((5, 0, [(124, 1)]), (21, 8, [(fragments[-1], 1)])):
        record = bytearray(struct.pack('>HBBII', 10, 0, 0, cnid, start)) + fork(0, mappings)[16:]
        extents.append(record)
    image[4 * block:4 * block + NODE] = tree_header(2, 1, 1, len(extents), 1, 1, [0, 1])
    image[4 * block + NODE:4 * block + 2 * NODE] = node(-1, 1, extents)[0]

    live = [catalog_record(1, 'Forensic', 2, directory=True), thread(2, 1, 'Forensic', True),
            catalog_record(2, 'fragmented.bin', 21, fork(9 * block, [(start, 1) for start in fragments[:8]], 9)),
            catalog_record(2, 'live.txt', 20, fork(15, [(80, 1)]), fork(8, [(120, 1)])),
            thread(20, 2, 'live.txt'), thread(21, 2, 'fragmented.bin')]
    catalog = 20 * block
    image[catalog:catalog + NODE] = tree_header(4, 1, 2, len(live), 2, 2, [0, 1, 2], 0xbc if sensitive else 0xcf)
    image[catalog + NODE:catalog + 2 * NODE] = node(0, 2, [key(1, 'Forensic') + struct.pack('>I', 2)])[0]
    leaf, locations, slack_at = node(-1, 1, live)
    slack_payload = b'Deleted from catalog slack\n'
    slack = catalog_record(2, 'slack.txt', 31, fork(len(slack_payload), [(114, 1)]))
    leaf[slack_at:slack_at + len(slack)] = slack
    image[catalog + 2 * NODE:catalog + 3 * NODE] = leaf
    deleted = [catalog_record(2, 'vanished.bin', 30, fork(2 * block, [(110, 1), (112, 1)])),
               catalog_record(2, 'gone', 32, directory=True),
               catalog_record(32, 'child.txt', 33, fork(6, [(118, 1)]))]
    dead, deleted_locations, _ = node(-1, 1, deleted)
    image[catalog + 3 * NODE:catalog + 4 * NODE] = dead

    name = 'demo'.encode('utf-16be')
    attr_key = struct.pack('>HHIIH', 12 + len(name), 0, 20, 0, len(name) // 2) + name
    attribute = attr_key + struct.pack('>II', 0x20, 0) + fork(9, [(122, 1)])
    image[52 * block:52 * block + NODE] = tree_header(2, 1, 1, 1, 1, 1, [0, 1])
    image[52 * block + NODE:52 * block + 2 * NODE] = node(-1, 1, [attribute])[0]

    struct.pack_into('>I', image, 69 * block, 1)
    struct.pack_into('>QQ', image, 69 * block + 36, 70 * block, 4 * block)
    journal = bytearray(44)
    struct.pack_into('>IIQQQIII', journal, 0, 0x4a4e4c78, 0x12345678, 512, 512, 4 * block, 512, 0, 512)
    struct.pack_into('>I', journal, 36, checksum(journal))
    image[70 * block:70 * block + len(journal)] = journal
    image[80 * block:80 * block + 15] = b'Live HFS+ file\n'
    for index, start in enumerate(fragments):
        image[start * block:(start + 1) * block] = bytes([65 + index]) * block
    image[110 * block:111 * block] = b'D' * block
    image[112 * block:113 * block] = b'E' * block
    image[114 * block:114 * block + len(slack_payload)] = slack_payload
    image[118 * block:118 * block + 6] = b'child\n'
    image[120 * block:120 * block + 8] = b'resource'
    image[122 * block:122 * block + 9] = b'attribute'
    image[126 * block:126 * block + 7] = b'orphan\n'
    manifest = {'block_size': block, 'node_size': NODE, 'catalog': catalog, 'bitmap': 3 * block,
                'overflow': 4 * block, 'attributes': 52 * block,
                'live_location': 2 * NODE + locations[3],
                'fragmented_location': 2 * NODE + locations[2],
                'deleted_locations': {'vanished.bin': 3 * NODE + deleted_locations[0],
                                      'gone': 3 * NODE + deleted_locations[1],
                                      'child.txt': 3 * NODE + deleted_locations[2],
                                      'slack.txt': 2 * NODE + slack_at}}
    manifest['ids'] = {name: (1 << 63) | location for name, location in manifest['deleted_locations'].items()}
    return image, manifest


def main():
    manifest = {}
    for name, block, sensitive in (('hfsplus', 512, False), ('hfsx', 512, True), ('hfsplus-4k', 4096, False)):
        image, info = build(block, sensitive)
        (HERE / (name + '.img.gz')).write_bytes(gzip.compress(image, mtime=0))
        manifest[name] = info
        print(name, len(image), len(gzip.compress(image, mtime=0)), 'compressed bytes')
    image, info = build()
    outer = bytearray(16384) + image
    struct.pack_into('>H', outer, 1024, 0x4244)
    struct.pack_into('>I', outer, 1024 + 20, 4096)
    struct.pack_into('>H', outer, 1024 + 28, 16)
    struct.pack_into('>HHH', outer, 1024 + 124, 0x482b, 2, 32)
    (HERE / 'wrapped.img.gz').write_bytes(gzip.compress(outer, mtime=0))
    manifest['wrapped'] = dict(info, embedded_offset=16384)
    (HERE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
