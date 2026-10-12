#!/usr/bin/env python3
# Zero e_shoff, e_shnum and e_shstrndx, so only the program headers remain.
#   python3 mknoshdr.py ext_tls ext_tls-noshdr
import shutil
import struct
import sys


def main(src, dst):
    with open(src, "rb") as f:
        elf = bytearray(f.read())
    if elf[:4] != b"\x7fELF":
        sys.exit("not an ELF")
    end = "<" if elf[5] == 1 else ">"
    if elf[4] == 2:
        struct.pack_into(end + "Q", elf, 0x28, 0)
        struct.pack_into(end + "HH", elf, 0x3c, 0, 0)
    else:
        struct.pack_into(end + "I", elf, 0x20, 0)
        struct.pack_into(end + "HH", elf, 0x30, 0, 0)
    with open(dst, "wb") as f:
        f.write(elf)
    shutil.copymode(src, dst)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
