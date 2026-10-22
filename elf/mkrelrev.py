#!/usr/bin/env python3
"""Copy an ELF32 rel object with the entries of every .rel.* section reversed."""
import shutil
import struct
import sys


def main(src, dst):
    with open(src, 'rb') as f:
        data = bytearray(f.read())
    le = data[5] == 1
    e = '<' if le else '>'
    shoff, = struct.unpack_from(e + 'I', data, 0x20)
    shentsize, shnum = struct.unpack_from(e + 'HH', data, 0x2e)
    for i in range(shnum):
        off = shoff + i * shentsize
        sh_type, = struct.unpack_from(e + 'I', data, off + 4)
        if sh_type != 9:  # SHT_REL
            continue
        sh_offset, sh_size = struct.unpack_from(e + 'II', data, off + 16)
        ents = [data[sh_offset + j:sh_offset + j + 8] for j in range(0, sh_size, 8)]
        data[sh_offset:sh_offset + sh_size] = b''.join(reversed(ents))
    with open(dst, 'wb') as f:
        f.write(data)
    shutil.copymode(src, dst)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
