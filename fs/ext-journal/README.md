# Retained ext3/ext4 journal records

Each gzip file is about 5–7 KiB and expands to a 4 MiB filesystem created by
mke2fs/debugfs. The generator writes deterministic transaction layouts into the
existing internal journal; journal block mappings come from debugfs so the
fixtures also exercise fragmented journal files. `manifest.json` records those
mappings for mutation tests.

- `ext3`: legacy JBD tags without checksums.
- `ext3-crc`: legacy transaction CRC32 checksums.
- `ext4-v2`: 64-bit JBD2 tags and checksum v2.
- `ext4-v3`: 64-bit JBD2 tags and checksum v3.
- `ext4-wrap`: a committed transaction crossing the ring boundary.
- `ext4-wrap-revoke`: the revoke block precedes a descriptor across the boundary.

The normal fixtures contain committed transaction 99 with an old file-data
block, transaction 100 with the inode-table block containing inode 13, an escaped
block in transaction 101, and a revoked block in transaction 102. Transaction 103
has no commit and must not be recovered. Inode 13's current size is zero; its
retained journal version has 28 bytes: `Deleted through the journal\n`.
The journal superblock marks the active log empty, so recovery must inspect
retained checkpointed records as well as the active replay log.

Run `python3 generate.py` with e2fsprogs installed to rebuild the images.
