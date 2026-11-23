#!/usr/bin/env python3
"""Generate a small ext2 image with a sparse file crossing the 4 GiB boundary."""
from pathlib import Path
import gzip
import struct
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
BLOCK = 4096
SIZE = 0x100000011

with tempfile.TemporaryDirectory() as temporary:
    image_path = Path(temporary) / "large.img"
    image_path.write_bytes(bytes(512 * 1024))
    subprocess.run(["mke2fs", "-q", "-F", "-t", "ext2", "-b", str(BLOCK),
                    "-I", "128", "-N", "32", "-O", "none", "-m", "0",
                    "-U", "12345678-1234-5678-1234-567812345678", str(image_path)], check=True)
    subprocess.run(["debugfs", "-w", "-R", "write /dev/null /large", str(image_path)], check=True)
    image = bytearray(image_path.read_bytes())


def u32(offset):
    return struct.unpack_from("<I", image, offset)[0]


def put32(offset, value):
    struct.pack_into("<I", image, offset, value)


bitmap = u32(BLOCK) * BLOCK
inode_table = u32(BLOCK + 8) * BLOCK
inode_size = struct.unpack_from("<H", image, 1024 + 88)[0]
# debugfs allocates the first non-reserved inode, number 12.
inode = inode_table + 11 * inode_size
assert struct.unpack_from("<H", image, inode)[0] & 0xf000 == 0x8000
allocated = []
for block in range(u32(1024 + 4)):
    byte, bit = bitmap + block // 8, 1 << (block & 7)
    if not image[byte] & bit:
        image[byte] |= bit
        allocated.append(block)
        if len(allocated) == 5:
            break
assert len(allocated) == 5
head, before, after, outer, inner = allocated
put32(1024 + 12, u32(1024 + 12) - len(allocated))
free_group = struct.unpack_from("<H", image, BLOCK + 12)[0]
struct.pack_into("<H", image, BLOCK + 12, free_group - len(allocated))
put32(1024 + 100, u32(1024 + 100) | 2)
put32(inode + 4, SIZE & 0xffffffff)
put32(inode + 108, SIZE >> 32)
put32(inode + 28, len(allocated) * (BLOCK // 512))
put32(inode + 40, head)
put32(inode + 40 + 13 * 4, outer)
for logical, physical in ((0xffffffff // BLOCK, before), (0x100000000 // BLOCK, after)):
    index = logical - 12 - BLOCK // 4
    put32(outer * BLOCK + (index // (BLOCK // 4)) * 4, inner)
    put32(inner * BLOCK + (index % (BLOCK // 4)) * 4, physical)
image[head * BLOCK:head * BLOCK + 5] = b"HEAD\n"
image[(before + 1) * BLOCK - 8:(before + 1) * BLOCK] = b"BEFORE!\n"
image[after * BLOCK:after * BLOCK + 17] = b"AFTER-4G:THE-END\n"
(HERE / "large.img.gz").write_bytes(gzip.compress(image, mtime=0))
print(f"Stored {len(image)} image bytes as {(HERE / 'large.img.gz').stat().st_size} gzip bytes")
