# Ext4 recovery fixture

`recovery.img.gz` is about 14 KiB compressed and expands to an 8 MiB ext4
filesystem. Regenerate it with `python3 generate.py` and e2fsprogs.

The image has 1 KiB blocks, 256-byte inodes, 64-bit group descriptors,
metadata checksums, flex groups and uninitialized inode/block bitmaps.

- `/live`, inode 12: `Live ext4 file\n`.
- Deleted `/vanished`, inode 13: 13 KiB with seven initialized extents and six
  sparse holes. Logical blocks 0, 2, 4, 6, 8, 10 and 12 contain repeated
  `A`, `C`, `E`, `G`, `I`, `K` and `M`, respectively. An external extent leaf
  at block 303 survives, as do the inode and deleted directory name.
- `/unwritten`, inode 14: one initialized block followed by three unwritten
  blocks, logical size 4096 bytes.
- `/link`, inode 15: a fast symlink to `live`.

The deleted inode and its eight physical blocks have clear allocation bits.
The fixture deliberately retains metadata via debugfs removal. Ordinary Linux
ext4 deletion can clear extent roots; recovering those requires journal history.
