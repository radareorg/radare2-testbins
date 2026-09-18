#!/usr/bin/env python3
# Build s390-31-globdat.so, an ELFCLASS32 (31-bit) s390 DSO with a RELATIVE and
# a GLOB_DAT in adjacent 4-byte slots. No toolchain here targets 31-bit s390,
# so a ppc32 DSO of the same shape is retargeted:
# (build steps in s390-31-globdat.s)
#   python3 mks390-31.py s390-31-ppc32.so s390-31-globdat.so
import struct
import sys

R_390_GLOB_DAT = 10
R_390_RELATIVE = 12
R_PPC_RELATIVE = 22
EM_S390 = 22
DT_RELACOUNT = 0x6ffffff9


def retarget(d):
    struct.pack_into(">H", d, 18, EM_S390)
    shoff = struct.unpack_from(">I", d, 32)[0]
    shentsize, shnum = struct.unpack_from(">HH", d, 46)
    for i in range(shnum):
        _, typ, _, _, off, size = struct.unpack_from(">IIIIII", d, shoff + i * shentsize)
        if typ != 4:
            continue
        for r in range(off, off + size, 12):
            info = struct.unpack_from(">I", d, r + 4)[0]
            if info & 0xff == R_PPC_RELATIVE:
                struct.pack_into(">I", d, r + 4, (info & ~0xff) | R_390_RELATIVE)


def glob_dat_beside_relative(d):
    # RELATIVE first in table order, then a GLOB_DAT on the slot below it
    struct.pack_into(">III", d, 0x1ac, 0x30234, R_390_RELATIVE, 0x30234)
    struct.pack_into(">III", d, 0x1ac + 12, 0x30230, (1 << 8) | R_390_GLOB_DAT, 0)
    for i in range(0x1c8, 0x1c8 + 0x68, 8):
        tag, _ = struct.unpack_from(">II", d, i)
        if tag == DT_RELACOUNT:
            struct.pack_into(">II", d, i, tag, 1)


def main():
    with open(sys.argv[1], "rb") as f:
        d = bytearray(f.read())
    retarget(d)
    glob_dat_beside_relative(d)
    with open(sys.argv[2], "wb") as f:
        f.write(d)


if __name__ == "__main__":
    main()
