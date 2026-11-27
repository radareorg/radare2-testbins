# Compact HFS+/HFSX forensic fixtures

Run `python3 generate.py` to regenerate these deterministic images. The generator
uses only Python's standard library; it writes the documented HFS+ structures
explicitly rather than mounting a volume or simulating a deletion on macOS.
No expanded image is checked in. All six gzip images together are under 9 KiB.

- `hfsplus.img.gz`: 128 KiB logical volume, 512-byte allocation blocks.
- `hfsx.img.gz`: the same layout with HFSX signature/version and binary name comparison.
- `hfsplus-4k.img.gz`: 1 MiB logical volume with 4096-byte allocation blocks.
- `wrapped.img.gz`: the first volume embedded at byte 16384 in an HFS wrapper.
- `names-forks.img.gz`: a 128 KiB volume extending the first layout with Unicode
  names, file/directory hard links, retained threads and recoverable attributes.
- `journal.img.gz`: a 128 KiB volume with two checksummed historical catalog
  versions, separate overflow extents, resource forks and directory ancestry.

All B-tree nodes are 4096 bytes. In the original four images, the catalog has a header, an index, one live
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

The names/forks image adds a fragmented catalog and attributes file. Its
`linked.txt` and `linked-again.txt` aliases share `iNode1234` in the private
file-link directory; `linked-dir` resolves to `dir_41` in the private directory-link
folder. Creation dates and Finder/BSD link metadata identify their backing
records. Unicode cases cover decomposed Latin, Greek, Hangul and escaped path
characters. `unlinked.txt` retains a deleted backing inode and resource fork;
`removed-but-linked.txt` points to a surviving live inode and must not recover.
Retained directory threads restore `lost-dir/child.txt`, while two conflicting
directory versions leave `ambiguous-child` unattached. A file thread without its
catalog file record supplies a name but no recoverable contents.

The attributes tree contains live inline and fragmented external values,
attributes on hard-link backing records, retained inline and nonresident values,
two historical versions sharing a name, a removed attribute on a live file and
an orphan inline attribute. The manifest records catalog and attribute-file
logical locations for deterministic mutation tests. Stream IDs are enumerated
from the mounted snapshot, separate from catalog candidate IDs.

The journal image relocates its internal journal to blocks 128 through 223.
Two completed transactions (sequences 41 and 42) retain `journal.bin` (CNID 40),
`history-dir` (CNID 41) and `history-dir/child.txt` (CNID 42). The first eight data
blocks are shared; same-transaction overflow records select block 116 (`I`) or
117 (`Z`) as the ninth block. Separate resource forks use blocks 118 and 119.
The historical tree targets are the current catalog's free leaf and the current
overflow leaf; their live on-disk versions are not replaced. Journal candidates
receive mounted-snapshot IDs with bits 63 and 62 set. The generator also builds
wrapped, little-endian, pending and continuation-header variants in memory for
the scripted tests. The journal fixture compresses to 1,354 bytes.

Journal layout and checksum rules follow Apple's published
[journal structures](https://github.com/apple-oss-distributions/hfs/blob/main/core/hfs_journal.h)
and [journal implementation](https://github.com/apple-oss-distributions/hfs/blob/main/core/hfs_journal.c).
