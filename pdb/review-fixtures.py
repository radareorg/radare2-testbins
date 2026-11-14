#!/usr/bin/env python3
"""Reproduce malformed and reordered variants used by the PDB review regressions."""
from pathlib import Path

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
