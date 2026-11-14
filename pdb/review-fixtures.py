#!/usr/bin/env python3
"""Reproduce malformed and reordered variants used by the PDB review regressions."""
from pathlib import Path
import struct

root = Path(__file__).resolve().parent
original = (root / 'SimplePDB.pdb').read_bytes()
assert original[0x2609e:].startswith(b'?SomeCoolFunction@@YAXXZ\0')
empty = bytearray(original)
empty[0x2609e] = 0
empty[0x26042:0x2604e] = b' ' * 12
(root / 'SimplePDB-empty-names.pdb').write_bytes(empty)

# Put the forward thunk before its target without changing the public records.
forward = bytearray(original)
forward[0x2607c:0x260b8] = original[0x26090:0x260b8] + original[0x2607c:0x26090]
(root / 'SimplePDB-thunk-first.pdb').write_bytes(forward)

# Incremental links may keep the GUID while increasing the age.
age4 = bytearray(original)
struct.pack_into('<I', age4, 66 * 4096 + 8, 4)
struct.pack_into('<I', age4, 39 * 4096 + 8, 4)
store = root / 'symbols/SimplePDB.pdb/1516D2A3E6864C06BD82C50FBE6152364'
store.mkdir(parents=True, exist_ok=True)
(store / 'SimplePDB.pdb').write_bytes(age4)
exe = bytearray((root / 'SimplePDB.exe').read_bytes())
rsds = exe.index(b'RSDS')
assert struct.unpack_from('<I', exe, rsds + 20)[0] == 3
struct.pack_into('<I', exe, rsds + 20, 4)
(root / 'SimplePDB-age4.exe').write_bytes(exe)


def record(kind, payload):
    return struct.pack('<HH', len(payload) + 2, kind) + payload


def public(name, offset):
    return record(0x110e, struct.pack('<IIH', 2, offset, 1) + name.encode() + b'\0')


def procedure(name, offset):
    return record(0x1110, struct.pack('<8IHB', 0, 0, 0, 6, 0, 0, 0x1000, offset, 1, 0) + name.encode() + b'\0')


def msf(streams):
    page_size = 1024
    counts = [(len(s) + page_size - 1) // page_size for s in streams]
    directory_size = 4 + len(streams) * 4 + sum(counts) * 4
    root_count = (directory_size + page_size - 1) // page_size
    assert root_count * 4 <= page_size
    page = 3 + root_count
    directory = struct.pack('<I', len(streams)) + struct.pack('<' + 'I' * len(streams), *map(len, streams))
    payload = bytearray()
    for stream, count in zip(streams, counts):
        directory += struct.pack('<' + 'I' * count, *range(page, page + count))
        payload += stream + bytes(count * page_size - len(stream))
        page += count
    header = original[:32] + struct.pack('<6I', page_size, 1, page, directory_size, 0, 2)
    blockmap = struct.pack('<' + 'I' * root_count, *range(3, 3 + root_count))
    return (header.ljust(page_size * 2, b'\0') + blockmap.ljust(page_size, b'\0')
            + directory.ljust(root_count * page_size, b'\0') + payload)


def synthetic_pdb(publics, modules, mappings=(), module_indices=None):
    info = bytearray(original[66 * 4096:66 * 4096 + 32])
    struct.pack_into('<I', info, 28, 0)
    modifier = record(0x1001, struct.pack('<IH', 0x74, 0))
    tpi = struct.pack('<5I', 20040203, 56, 0x1000, 0x1001, len(modifier)) + bytes(36) + modifier
    module_info = bytearray()
    module_streams = []
    for index, procs in enumerate(modules, 7):
        stream = struct.pack('<I', 4) + b''.join(procedure(name, offset) for name, offset in procs)
        entry = bytearray(64)
        stream_index = module_indices[index - 7] if module_indices else index
        struct.pack_into('<hI', entry, 34, stream_index, len(stream))
        entry += b'module\0object\0'
        entry += bytes(-len(entry) % 4)
        module_info += entry
        module_streams.append(stream)
    dbi = bytearray(64)
    struct.pack_into('<III', dbi, 0, 0xffffffff, 19990903, 3)
    struct.pack_into('<h', dbi, 12, -1)
    struct.pack_into('<h', dbi, 16, -1)
    struct.pack_into('<h', dbi, 20, 4)
    struct.pack_into('<I', dbi, 24, len(module_info))
    struct.pack_into('<I', dbi, 48, 22)
    dbi += module_info + struct.pack('<11h', -1, -1, -1, -1, 6 if mappings else -1, 5, -1, -1, -1, -1, -1)
    section = b'.text\0\0\0' + struct.pack('<6I2HI', 0x1000, 0x1000, 0x1000, 0, 0, 0, 0, 0, 0x60000020)
    return msf([bytes(4), info, tpi, dbi, b''.join(public(name, off) for name, off in publics), section,
                b''.join(struct.pack('<II', src, dst) for src, dst in mappings)] + module_streams)


(root / 'omap-symbol-addresses.pdb').write_bytes(synthetic_pdb(
    [('valid', 0), ('alias', 0), ('deleted', 0x10), ('missing', 0x20),
     ('overflow', 0xfffff100), ('high', 0x30)],
    [[('module_valid', 0x40), ('module_deleted', 0x50), ('module_missing', 0x60),
      ('module_overflow', 0xfffff100), ('module_high', 0x70)]],
    [(0x1000, 0x2000), (0x1010, 0), (0x1030, 0x80000000),
     (0x1040, 0x3000), (0x1050, 0), (0x1070, 0x80001000)]))

(root / 'many-module-streams.pdb').write_bytes(synthetic_pdb(
    [], [[(f'module_{i}', i * 16)] for i in range(16384)]))
(root / 'module-parser-indices.pdb').write_bytes(synthetic_pdb(
    [('public', 0)], [[('first', 0x10)], [('duplicate', 0x20)], [('invalid', 0x30)]],
    module_indices=[7, 7, 32767]))
