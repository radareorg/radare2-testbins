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
