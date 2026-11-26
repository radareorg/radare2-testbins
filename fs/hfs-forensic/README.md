# Compact classic HFS forensic fixtures

Run `python3 generate.py` to recreate these deterministic volumes using Python's
standard library. No mounting, macOS tools or expanded image is needed. Both
gzip images together occupy less than 2 KiB.

- `hfs.img.gz`: 128 allocation blocks of 512 bytes, with a 512-byte B-tree node size.
- `hfs-1536.img.gz`: the same records with 1536-byte allocation blocks. The
  allocation area starts at sector 5, testing non-aligned allocation origins.

The catalog has an index and three live leaves. Free leaves retain deleted
file/folder records and threads; live-leaf slack retains another deleted file.
The extents-overflow tree has current file/bad-block mappings and one retained
deleted-file continuation. The manifest records logical catalog locations,
candidate IDs, allocation geometry and exact active-leaf slack regions.

Live catalog records include `live.txt` (CNID 20), a four-fragment file (21),
MacRoman `café` (22) and an empty file (23). The live file has a resource fork,
tail slack and an additional preallocated block beyond logical EOF.

Deleted `vanished.bin` (CNID 30) has three inline fragments and a retained
overflow fragment, plus a resource fork. A file thread preserves its name even
after the catalog key's name length is cleared. Other evidence includes
`gone/child.txt`, `lost-dir/lost-child`, `slack.txt` and a file thread whose
file record no longer survives. The last supplies a name, not file contents.

Block 94 belongs to the bad-block file; block 96 is allocated without a live
owner. Free block 100 contains `FREE HFS EVIDENCE\n`. Data/resource/slack blocks
are distinct so mutation tests can check allocation reuse and hidden ownership
independently. A copy of the MDB near the end of each image supports tests of
alternate volume metadata recovery.

In radare2, `test/db/cmd/cmd_fs_hfs_forensic` checks the command output and
`test/scripts/test-hfs-io.py` uses the manifest to exercise reads and recovery
after changing specific metadata fields.
