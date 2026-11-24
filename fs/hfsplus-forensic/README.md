# Compact HFS+/HFSX forensic fixtures

Run `python3 generate.py` to regenerate these deterministic images. The generator
uses only Python's standard library; it writes the documented HFS+ structures
explicitly rather than mounting a volume or simulating a deletion on macOS.
No expanded image is checked in. All four gzip images together are under 6 KiB.

- `hfsplus.img.gz`: 128 KiB logical volume, 512-byte allocation blocks.
- `hfsx.img.gz`: the same layout with HFSX signature/version and binary name comparison.
- `hfsplus-4k.img.gz`: 1 MiB logical volume with 4096-byte allocation blocks.
- `wrapped.img.gz`: the first volume embedded at byte 16384 in an HFS wrapper.

All B-tree nodes are 4096 bytes. The catalog has a header, an index, one live
leaf and a free leaf retaining deleted records. Its header allocation map marks
only the first three nodes allocated. Live-leaf slack also retains a deleted
file record. The extents and attributes trees each have a header and a live leaf.

Live catalog IDs:

- CNID 2: root `Forensic`.
- CNID 20: `live.txt`, containing `Live HFS+ file\n`; its resource fork owns block 120.
- CNID 21: `fragmented.bin`, nine blocks `A` through `I`. Eight inline extents
  map blocks 82, 84, ..., 96; an overflow record maps the ninth block at 98.

Retained catalog records:

- CNID 30: `vanished.bin`, free data blocks 110 and 112 containing `D` and `E`.
- CNID 31: `slack.txt`, a record in live-leaf slack; block 114 contains
  `Deleted from catalog slack\n`.
- CNID 32: deleted directory `gone`.
- CNID 33: `gone/child.txt`, block 118 containing `child\n`.

Deleted-entry API IDs are `0x8000000000000000 | catalog-byte-offset`, not CNIDs.
`manifest.json` records their locations and IDs. This distinguishes retained
versions and lets recovery reject a candidate whose CNID has a live owner.

The attributes tree owns an external attribute in block 122. The bad-block file
owns block 124. Block 126 is allocated without a current owner. Startup metadata
owns block 68. A journal-info block at 69 describes an empty, checksummed journal
in blocks 70 through 73. This deliberately small journal exercises the reader's
clean-state and ownership checks; it is not an operating-system journal workload.
