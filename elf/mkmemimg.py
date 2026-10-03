#!/usr/bin/env python3
# Lay an ELF out the way a loader maps it: each PT_LOAD at p_vaddr - base,
# up to p_memsz, with the section table zeroed. base is the vaddr of the
# PT_LOAD that maps the ELF header.
#   python3 mkmemimg.py simple-hello-world-with-wrong-rela-section-name x86_64-pie-memimg
#   python3 mkmemimg.py x86_64-tailrela.so x86_64-tailrela-memimg
import struct
import sys


def main(src, dst, size=None):
    with open(src, "rb") as f:
        elf = f.read()
    if elf[:4] != b"\x7fELF":
        sys.exit("not an ELF")
    is64 = elf[4] == 2
    end = "<" if elf[5] == 1 else ">"
    if is64:
        phoff, = struct.unpack_from(end + "Q", elf, 0x20)
        phentsize, phnum = struct.unpack_from(end + "HH", elf, 0x36)
        fmt = end + "IIQQQQQQ"
    else:
        phoff, = struct.unpack_from(end + "I", elf, 0x1c)
        phentsize, phnum = struct.unpack_from(end + "HH", elf, 0x2a)
        fmt = end + "IIIIIIII"
    loads = []
    for i in range(phnum):
        f = struct.unpack_from(fmt, elf, phoff + i * phentsize)
        if is64:
            p_type, _, p_offset, p_vaddr, _, p_filesz, p_memsz, _ = f
        else:
            p_type, p_offset, p_vaddr, _, p_filesz, p_memsz, _, _ = f
        if p_type == 1:
            loads.append((p_offset, p_vaddr, p_filesz, p_memsz))
    base = [v for o, v, _, _ in loads if o == 0]
    if not base:
        sys.exit("no PT_LOAD maps the ELF header")
    base = base[0]
    img = bytearray(max(v + m for _, v, _, m in loads) - base)
    for off, vaddr, filesz, _ in loads:
        img[vaddr - base:vaddr - base + filesz] = elf[off:off + filesz]
    if is64:
        struct.pack_into(end + "Q", img, 0x28, 0)
        struct.pack_into(end + "HHH", img, 0x3a, 0, 0, 0)
    else:
        struct.pack_into(end + "I", img, 0x20, 0)
        struct.pack_into(end + "HHH", img, 0x2e, 0, 0, 0)
    if size is not None:
        img = img[:size]
    with open(dst, "wb") as f:
        f.write(img)


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        sys.exit("usage: mkmemimg.py in.elf out.img [size]")
    main(sys.argv[1], sys.argv[2], int(sys.argv[3], 0) if len(sys.argv) == 4 else None)
