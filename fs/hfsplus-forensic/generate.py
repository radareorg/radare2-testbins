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


def attribute_key(cnid, name, start=0):
    encoded = name.encode('utf-16be')
    return struct.pack('>HHIIH', 12 + len(encoded), 0, cnid, start, len(encoded) // 2) + encoded


def inline_attribute(cnid, name, data):
    return attribute_key(cnid, name) + struct.pack('>IIII', 0x10, 0, 0, len(data)) + data


def build_names_forks():
    image, original = build()
    block = 512
    epoch = 2082844800 + 1700000000

    def record(parent, name, cnid, data=None, resource=None, directory=False, created=None):
        result = bytearray(catalog_record(parent, name, cnid, data, resource, directory))
        offset = len(key(parent, name))
        struct.pack_into('>I', result, offset + 12, epoch - 500 if created is None else created)
        return result

    def link(parent, name, cnid, reference, directory=False):
        result = record(parent, name, cnid, created=epoch - 900)
        offset = len(key(parent, name))
        struct.pack_into('>H', result, offset + 2, 0x20)
        struct.pack_into('>III', result, offset + 44, reference,
                         0x66647270 if directory else 0x686c6e6b,
                         0x4d414353 if directory else 0x6866732b)
        return result

    private_name = '\0\0\0\0HFS+ Private Data'
    dir_private_name = '.HFS+ Private Directory Data\r'
    mappings = {'linked_data': 128, 'linked_resource': 129, 'directory_child': 130,
                'unicode': 131, 'greek': 132, 'hangul': 133, 'escaped': 134,
                'deleted_link_data': 135, 'deleted_link_resource': 136,
                'lost_child': 137, 'ambiguous_child': 138}
    contents = {'linked_data': b'Hard link contents\n', 'linked_resource': b'Linked resource\n',
                'directory_child': b'directory child\n', 'unicode': b'unicode\n',
                'greek': b'greek\n', 'hangul': b'hangul\n', 'escaped': b'escaped\n',
                'deleted_link_data': b'Recovered linked file\n', 'deleted_link_resource': b'Recovered resource\n',
                'lost_child': b'lost child\n', 'ambiguous_child': b'ambiguous child\n'}
    for name, start in mappings.items():
        image[start * block:start * block + len(contents[name])] = contents[name]

    def payload(name):
        return fork(len(contents[name]), [(mappings[name], 1)])

    live = [record(1, 'Forensic', 2, directory=True, created=epoch - 1000),
            thread(2, 1, 'Forensic', True),
            record(2, private_name, 16, directory=True, created=epoch - 900),
            record(2, dir_private_name, 17, directory=True, created=epoch - 900),
            record(2, 'fragmented.bin', 21, fork(9 * block, [(82 + i * 2, 1) for i in range(8)], 9)),
            record(2, 'live.txt', 20, fork(15, [(80, 1)]), fork(8, [(120, 1)])),
            link(2, 'linked.txt', 22, 1234), link(2, 'linked-again.txt', 23, 1234),
            link(2, 'linked-dir', 24, 41, True),
            record(2, 'Cafe\u0301.txt', 43, payload('unicode')),
            record(2, '\u03b1\u03b8\u03b7\u03bd\u03b1', 44, payload('greek')),
            record(2, '\u1100\u1161.txt', 45, payload('hangul')),
            record(2, 'percent%/file', 46, payload('escaped')),
            record(16, 'iNode1234', 40, payload('linked_data'), payload('linked_resource')),
            record(17, 'dir_41', 41, directory=True),
            record(41, 'inside.txt', 42, payload('directory_child')),
            thread(20, 2, 'live.txt'), thread(21, 2, 'fragmented.bin'),
            thread(22, 2, 'linked.txt'), thread(23, 2, 'linked-again.txt'),
            thread(24, 2, 'linked-dir'), thread(40, 16, 'iNode1234'),
            thread(41, 17, 'dir_41', True)]
    live.sort(key=lambda value: (struct.unpack_from('>I', value, 2)[0], bytes(value[8:2 + struct.unpack_from('>H', value)[0]])))
    chunks, current = [], []
    for value in live:
        required = 14 + sum((len(item) + 1) & ~1 for item in current + [value]) + 2 * (len(current) + 2)
        if required > NODE - 320:
            chunks.append(current)
            current = []
        current.append(value)
    chunks.append(current)
    assert len(chunks) <= 3
    leaf_ids = [2, 4, 5][:len(chunks)]
    catalog = 20 * block
    image[catalog:catalog + NODE] = tree_header(8, 1, 2, len(live), leaf_ids[0], leaf_ids[-1], [0, 1] + leaf_ids)
    index = [value[0][:2 + struct.unpack_from('>H', value[0])[0]] + struct.pack('>I', leaf_id)
             for value, leaf_id in zip(chunks, leaf_ids)]
    image[catalog + NODE:catalog + 2 * NODE] = node(0, 2, index)[0]
    locations = {}
    slack_location = None

    def catalog_address(number):
        return catalog + number * NODE if number < 4 else 160 * block + (number - 4) * NODE

    for order, (leaf_id, chunk) in enumerate(zip(leaf_ids, chunks)):
        leaf, offsets, free_at = node(-1, 1, chunk, leaf_ids[order + 1] if order + 1 < len(leaf_ids) else 0,
                               leaf_ids[order - 1] if order else 0)
        if order + 1 == len(leaf_ids):
            slack = record(2, 'slack.txt', 31, fork(27, [(114, 1)]))
            assert free_at + len(slack) < NODE - (len(chunk) + 1) * 2
            leaf[free_at:free_at + len(slack)] = slack
            slack_location = leaf_id * NODE + free_at
        image[catalog_address(leaf_id):catalog_address(leaf_id) + NODE] = leaf
        for value, offset in zip(chunk, offsets):
            kind = struct.unpack_from('>H', value, 2 + struct.unpack_from('>H', value)[0])[0]
            if kind in (1, 2):
                cnid = struct.unpack_from('>I', value, 10 + struct.unpack_from('>H', value)[0])[0]
                locations[str(cnid)] = leaf_id * NODE + offset

    deleted = [record(16, 'iNode5678', 50, payload('deleted_link_data'), payload('deleted_link_resource')),
               link(2, 'unlinked.txt', 51, 5678), link(2, 'removed-but-linked.txt', 52, 1234),
               thread(53, 2, 'thread-only.txt'), thread(54, 2, 'lost-dir', True),
               record(54, 'child.txt', 55, payload('lost_child')),
               record(2, 'old-a', 60, directory=True, created=epoch - 700),
               record(2, 'old-b', 60, directory=True, created=epoch - 600),
               record(60, 'ambiguous-child', 61, payload('ambiguous_child'))]
    leaf, offsets, _ = node(-1, 1, deleted)
    image[catalog_address(6):catalog_address(6) + NODE] = leaf
    deleted_ids = dict(original['ids'])
    deleted_ids['slack.txt'] = (1 << 63) | slack_location
    deleted_locations = dict(original['deleted_locations'], **{'slack.txt': slack_location})
    for value, offset in zip(deleted, offsets):
        size = struct.unpack_from('>H', value)[0]
        parent, nlen = struct.unpack_from('>IH', value, 2)
        kind = struct.unpack_from('>H', value, size + 2)[0]
        name = value[8:8 + nlen * 2].decode('utf-16be')
        if kind in (3, 4):
            v = size + 2
            nlen = struct.unpack_from('>H', value, v + 8)[0]
            name = value[v + 10:v + 10 + nlen * 2].decode('utf-16be')
        if parent == 54 and kind in (1, 2):
            name = 'lost-dir/' + name
        deleted_ids[name] = (1 << 63) | (6 * NODE + offset)
        deleted_locations[name] = 6 * NODE + offset

    descriptor = 1024 + 272
    image[descriptor:descriptor + 80] = fork(8 * NODE, [(20, 4 * NODE // block), (160, 4 * NODE // block)])
    attrs = [inline_attribute(20, 'com.example.inline', b'inline attr\n'),
             attribute_key(20, 'com.example.fragmented') + struct.pack('>II', 0x20, 0) + fork(600, [(139, 1)], 2),
             attribute_key(20, 'com.example.fragmented', 1) + struct.pack('>II', 0x30, 0) + fork(0, [(141, 1)])[16:],
             attribute_key(20, 'demo') + struct.pack('>II', 0x20, 0) + fork(9, [(122, 1)]),
             inline_attribute(40, 'user.linked', b'linked attr\n')]
    attrs.sort(key=lambda value: (struct.unpack_from('>I', value, 4)[0], value[14:struct.unpack_from('>H', value)[0] + 2],
                                  struct.unpack_from('>I', value, 8)[0]))
    image[52 * block:52 * block + NODE] = tree_header(3, 1, 1, len(attrs), 1, 1, [0, 1])
    leaf, attr_offsets, _ = node(-1, 1, attrs)
    image[52 * block + NODE:52 * block + 2 * NODE] = leaf
    old = [attribute_key(30, 'user.deleted') + struct.pack('>II', 0x20, 0) + fork(14, [(142, 1)]),
           inline_attribute(30, 'user.inline', b'deleted inline\n'),
           attribute_key(20, 'user.removed') + struct.pack('>II', 0x20, 0) + fork(13, [(144, 1)]),
           inline_attribute(30, 'user.history', b'one\n'), inline_attribute(30, 'user.history', b'two\n'),
           inline_attribute(999, 'user.orphan', b'orphan attr\n'),
           attribute_key(30, 'user.big') + struct.pack('>II', 0x20, 0) + fork(700, [(146, 1)], 2),
           attribute_key(30, 'user.big', 1) + struct.pack('>II', 0x30, 0) + fork(0, [(148, 1)])[16:]]
    leaf, old_offsets, _ = node(-1, 1, old)
    image[192 * block:192 * block + NODE] = leaf
    image[1024 + 352:1024 + 432] = fork(3 * NODE, [(52, 2 * NODE // block), (192, NODE // block)])
    for number in list(range(160, 200)) + list(range(128, 135)) + [139, 141]:
        image[3 * block + number // 8] |= 128 >> (number % 8)
    image[139 * block:140 * block] = b'X' * block
    image[141 * block:142 * block] = b'Y' * block
    image[142 * block:142 * block + 14] = b'old attribute\n'
    image[144 * block:144 * block + 13] = b'removed attr\n'
    image[146 * block:147 * block] = b'G' * block
    image[148 * block:149 * block] = b'H' * block
    image[-1024:-512] = image[1024:1536]
    info = dict(original, ids=deleted_ids, deleted_locations=deleted_locations, live_locations=locations, leaf_ids=leaf_ids,
                active_attribute_locations=[NODE + offset for offset in attr_offsets],
                old_attribute_locations=[2 * NODE + offset for offset in old_offsets])
    return image, info


def journal_chunk(blocks, sequence, little=False, first=True, sector=512):
    order = '<' if little else '>'
    header = bytearray(sector)
    struct.pack_into(order + 'HHIII', header, 0, sector // 16 - 1, len(blocks) + 1,
                     sector + sum(len(data) for _, data in blocks), 0, 1 | (2 if first else 0))
    struct.pack_into(order + 'I', header, 28, sequence)
    for index, (target, data) in enumerate(blocks, 1):
        struct.pack_into(order + 'QII', header, 16 + index * 16, target // sector, len(data), checksum(data))
    struct.pack_into(order + 'I', header, 8, checksum(header[:32]))
    return header + b''.join(data for _, data in blocks)


def build_journal(block=512, sensitive=False, little=False, pending=False, wrap=False, split=False):
    image, info = build(block, sensitive)
    sector = 512
    offset, size = 128 * block, 96 * block
    struct.pack_into('>QQ', image, 69 * block + 36, offset, size)
    for bit in range(128, 224):
        image[3 * block + bit // 8] |= 128 >> (bit % 8)
    order = '<' if little else '>'
    position = size - 2 * sector if wrap else sector
    first = position
    chunks = []
    for version, sequence in enumerate((41, 42)):
        mappings = [(100 + index * 2, 1) for index in range(8)]
        data = fork(9 * block, mappings, 9)
        resource = b'Journal resource ' + (b'one' if not version else b'two') + b'\n'
        image[(118 + version) * block:(118 + version) * block + len(resource)] = resource
        records = [catalog_record(2, 'journal.bin', 40, data, fork(len(resource), [(118 + version, 1)])),
                   catalog_record(2, 'history-dir', 41, directory=True),
                   catalog_record(41, 'child.txt', 42, fork(6, [(115, 1)]))]
        leaf = node(-1, 1, records)[0]
        overflow = struct.pack('>HBBII', 10, 0, 0, 40, 8) + fork(0, [(116 + version, 1)])[16:]
        extra = node(-1, 1, [overflow])[0]
        targets = [(info['catalog'] + 3 * NODE, leaf), (info['overflow'] + NODE, extra)]
        if split:
            parts = [[(targets[0][0] + index * sector, leaf[index * sector:(index + 1) * sector])]
                     for index in range(NODE // sector)] + [[targets[1]]]
        else:
            parts = [targets]
        for index, items in enumerate(parts):
            payload = journal_chunk(items, sequence, little, index == 0, sector)
            chunks.append({'position': position, 'sequence': sequence, 'size': len(payload)})
            for byte in payload:
                image[offset + position] = byte
                position += 1
                if position == size:
                    position = sector
    journal = bytearray(48)
    struct.pack_into(order + 'IIQQQIIII', journal, 0, 0x4a4e4c78, 0x12345678,
                     first if pending else position, position, size, sector, 0, sector, 42)
    struct.pack_into(order + 'I', journal, 36, checksum(journal[:44]))
    image[offset:offset + 48] = journal
    for index in range(8):
        start = (100 + index * 2) * block
        image[start:start + block] = bytes([65 + index]) * block
    image[116 * block:117 * block] = b'I' * block
    image[117 * block:118 * block] = b'Z' * block
    image[115 * block:115 * block + 6] = b'child\n'
    return image, dict(info, journal_offset=offset, journal_size=size,
                       journal_start=first, journal_end=position, journal_chunks=chunks)


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
    image, info = build_names_forks()
    (HERE / 'names-forks.img.gz').write_bytes(gzip.compress(image, mtime=0))
    manifest['names-forks'] = info
    print('names-forks', len(image), len(gzip.compress(image, mtime=0)), 'compressed bytes')
    image, info = build_journal()
    (HERE / 'journal.img.gz').write_bytes(gzip.compress(image, mtime=0))
    manifest['journal'] = info
    print('journal', len(image), len(gzip.compress(image, mtime=0)), 'compressed bytes')
    (HERE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
