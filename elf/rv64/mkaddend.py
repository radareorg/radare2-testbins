#!/usr/bin/env python3
# Copy ls and give its R_RISCV_64 against the undefined weak
# _ITM_deregisterTMCloneTable (at 0x1b618) an addend of 16, the shape of
# `extern int arr[]; int *p = &arr[4];` in a shared object.
import shutil, struct, sys

R_RISCV_64 = 2
SITE = 0x1b618
ADDEND = 16

src, dst = sys.argv[1:3]
with open(src, 'rb') as f:
    d = bytearray(f.read())
assert d[:6] == b'\x7fELF\x02\x01', 'ELF64 LE expected'
e_shoff, = struct.unpack_from('<Q', d, 0x28)
e_shentsize, e_shnum = struct.unpack_from('<HH', d, 0x3a)
hits = 0
for i in range(e_shnum):
    sh = e_shoff + e_shentsize * i
    sh_type, = struct.unpack_from('<I', d, sh + 4)
    if sh_type != 4:  # SHT_RELA
        continue
    off, size = struct.unpack_from('<QQ', d, sh + 0x18)
    for e in range(off, off + size, 24):
        r_offset, r_info = struct.unpack_from('<QQ', d, e)
        if r_offset == SITE and (r_info & 0xffffffff) == R_RISCV_64:
            struct.pack_into('<q', d, e + 16, ADDEND)
            hits += 1
assert hits == 1, hits
with open(dst, 'wb') as f:
    f.write(d)
shutil.copymode(src, dst)
print('wrote', dst)
