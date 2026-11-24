# ext4 unwritten extent fixture

The compressed image is about 1 KiB and expands to a 512 KiB ext4 filesystem
with 1024-byte blocks, 128-byte inodes and no journal. Generate it with
e2fsprogs using `python3 generate.py`.

- `/live`, inode 12: `Live ext4 file\n` at block 17 (0x4400).
- Deleted `/old`: `Stale secret\n` repeated 315 times, written to blocks 18-21
  (0x4800-0x57ff) and then removed, leaving the bytes on disk.
- `/prealloc`, inode 13: 4096 bytes preallocated with `fallocate`. Its
  unwritten extents reuse blocks 18 and 20-22, so the stale bytes now sit in
  allocated blocks that read back as zeros through the file.
