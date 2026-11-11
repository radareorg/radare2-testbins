#!/usr/bin/env python3
# Hand-assembles minimal Mach-O MH_OBJECT files (one __TEXT,__text and one __DATA,__data section)
# with local, global, common, undefined and absolute symbols, to exercise symbol listing in radare2.
import struct, sys
N_UNDF, N_ABS, N_SECT, N_EXT = 0x0, 0x2, 0xe, 0x1
def build(arch):
    is64 = arch == 'arm64'
    if is64:
        magic, cpu, sub = 0xfeedfacf, 0x0100000c, 0
        nop = struct.pack('<I', 0xd503201f)
    else:
        magic, cpu, sub = 0xfeedface, 12, 9
        nop = struct.pack('<I', 0xe320f000)
    text = nop * 4          # 16 bytes at section address 0
    data = b'\x01\0\0\0\2\0\0\0'  # 8 bytes at section address 16
    # name, type, sect, value
    syms = [
        ('_lf',         N_SECT,         1, 0x00),   # local function in __text
        ('_sdata',      N_SECT,         2, 0x10),   # local datum in __data
        ('_main',       N_SECT | N_EXT, 1, 0x08),   # global function in __text
        ('_abs',        N_ABS | N_EXT,  0, 0x1000), # absolute, value >= 100
        ('_common_var', N_UNDF | N_EXT, 0, 4),      # common symbol: value is the size
        ('_ext',        N_UNDF | N_EXT, 0, 0),      # undefined
    ]
    strtab = b'\0'
    stridx = []
    for s in syms:
        stridx.append(len(strtab))
        strtab += s[0].encode() + b'\0'
    strtab += b'\0' * (-len(strtab) % 4)
    nl_size = 16 if is64 else 12
    seg_size = 72 if is64 else 56
    sect_size = 80 if is64 else 68
    ncmds = 3
    sizeofcmds = (seg_size + 2 * sect_size) + 24 + 80
    hdr_size = 32 if is64 else 28
    off_text = hdr_size + sizeofcmds
    off_data = off_text + len(text)
    off_sym = off_data + len(data)
    off_str = off_sym + nl_size * len(syms)
    if is64:
        hdr = struct.pack('<IiiIIIII', magic, cpu, sub, 1, ncmds, sizeofcmds, 0, 0)
        seg = struct.pack('<II16sQQQQiiII', 0x19, seg_size + 2 * sect_size, b'', 0, 24, off_text, 24, 7, 7, 2, 0)
        s1 = struct.pack('<16s16sQQIIIIIIII', b'__text', b'__TEXT', 0, len(text), off_text, 2, 0, 0, 0x80000400, 0, 0, 0)
        s2 = struct.pack('<16s16sQQIIIIIIII', b'__data', b'__DATA', 16, len(data), off_data, 2, 0, 0, 0, 0, 0, 0)
    else:
        hdr = struct.pack('<IiiIIIII', magic, cpu, sub, 1, ncmds, sizeofcmds, 0, 0)[:28]
        seg = struct.pack('<II16sIIIIiiII', 0x1, seg_size + 2 * sect_size, b'', 0, 24, off_text, 24, 7, 7, 2, 0)
        s1 = struct.pack('<16s16sIIIIIIIII', b'__text', b'__TEXT', 0, len(text), off_text, 2, 0, 0, 0x80000400, 0, 0)
        s2 = struct.pack('<16s16sIIIIIIIII', b'__data', b'__DATA', 16, len(data), off_data, 2, 0, 0, 0, 0, 0)
    symtab = struct.pack('<IIIIII', 0x2, 24, off_sym, len(syms), off_str, len(strtab))
    # locals 0..1, extdef 2..3, undef 4..5
    dysym = struct.pack('<II' + 'I' * 18, 0xb, 80, 0, 2, 2, 2, 4, 2, *([0] * 12))
    nl = b''
    for (name, t, sect, val), sx in zip(syms, stridx):
        if is64:
            nl += struct.pack('<IBBHQ', sx, t, sect, 0, val)
        else:
            nl += struct.pack('<IBBHI', sx, t, sect, 0, val)
    out = hdr + seg + s1 + s2 + symtab + dysym + text + data + nl + strtab
    assert len(out) == off_str + len(strtab)
    return out
for arch in ('arm64', 'armv7'):
    open(sys.argv[1] + '/objsyms-%s.o' % arch, 'wb').write(build(arch))
