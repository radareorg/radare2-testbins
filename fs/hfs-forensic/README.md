# Classic HFS recovery fixtures

Run `python3 generate.py` to regenerate both images and `manifest.json` without
platform tools. The images use 512-byte B-tree nodes, 128 allocation blocks and
an allocation origin at byte 2560. `hfs.img.gz` uses 512-byte allocation blocks;
`hfs-1536.img.gz` uses 1536-byte blocks to exercise non-power-of-two geometry.

The live catalog contains an empty file, a MacRoman filename, fragmented data,
and a file with data/resource fork slack. Free catalog nodes retain a deleted
file with an overflow extent and resource fork, a directory and child, and
file/directory threads with missing catalog records. An allocated leaf retains
`slack.txt` beyond its last active record. Allocation bits distinguish live
storage, orphan blocks, bad blocks and free space containing a search marker.

These fixtures serve `test/db/cmd/cmd_fs_hfs_forensic` and
`test/scripts/test-hfs-io.py` in radare2. The manifest records geometry, catalog
locations and recovery IDs so the I/O tests can mutate precise metadata fields.
