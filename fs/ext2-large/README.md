# Large sparse ext2 file

`large.img.gz` is a 512 KiB ext2 filesystem with 4096-byte blocks. Its `/large`
file has a logical length of 4,294,967,313 bytes (4 GiB + 17), while only three
file-data blocks and two indirect blocks are allocated. The stored gzip image
is under 1 KiB; no multi-gigabyte file is stored or created by the generator.

- Offset 0: `HEAD\n`.
- Offset 0xfffffff8: `BEFORE!\n`.
- Offset 0x100000000: `AFTER-4G:THE-END\n`, ending at EOF.
- Unallocated logical blocks are sparse holes.

Rebuild with `python3 generate.py` and e2fsprogs installed. The generator starts
with mke2fs/debugfs metadata and updates the inode, block maps and allocation
counts. Regression tests read the compressed image directly through `gzip://`.
