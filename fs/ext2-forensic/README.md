# Classic ext2 recovery fixture

The compressed image is about 1 KiB and expands to a 512 KiB ext2 filesystem
with 1024-byte blocks and 128-byte inodes. Generate it with e2fsprogs using
`python3 generate.py`.

- `/live`, inode 12: `Live ext2 file\n`, 15 bytes.
- Deleted `/vanished`, inode 13: `Recover ext2 data\n` repeated 1024 times,
  18432 bytes. Its name survives in root directory slack and its retained
  block map uses twelve direct blocks and one indirect block.

The inode and data block allocation bits for `/vanished` are clear. Recovery
must consult those bits rather than treating a retained pointer as ownership.
