#!/usr/bin/env python3
# Rewrite an llvm-mc --crel object into the implicit-addend CREL flavor:
# take reloc triples and in-place section words from a classic REL build of
# the same source, re-encode each .crel.* blob with the addend bit clear.
# CREL: header ULEB(count<<3|addendBit<<2|shift); entry byte0 =
# (delta_offset<<flagBits)|flags (flagBits = addendBit?3:2), then SLEB
# deltas for symidx (flag 1) and type (flag 2).
import struct, sys

def read_elf32(path):
    d = bytearray(open(path, 'rb').read())
    assert d[:6] == b'\x7fELF\x01\x01', 'ELF32 LE expected'
    e_shoff, = struct.unpack_from('<I', d, 0x20)
    e_shnum, = struct.unpack_from('<H', d, 0x30)
    e_shstrndx, = struct.unpack_from('<H', d, 0x32)
    secs = []
    for i in range(e_shnum):
        off = e_shoff + 40 * i
        name, typ, flags, addr, offset, size, link, info, align, entsize = \
            struct.unpack_from('<10I', d, off)
        secs.append(dict(hdr_off=off, name_off=name, type=typ, off=offset,
                         size=size, link=link, info=info, entsize=entsize))
    strtab = secs[e_shstrndx]
    for s in secs:
        end = d.index(b'\0', strtab['off'] + s['name_off'])
        s['name'] = d[strtab['off'] + s['name_off']:end].decode()
    return d, secs

def symtab_names(d, secs):
    st = next(s for s in secs if s['type'] == 2)  # SHT_SYMTAB
    str_off = secs[st['link']]['off']
    names = []
    for i in range(st['size'] // 16):
        n, = struct.unpack_from('<I', d, st['off'] + 16 * i)
        end = d.index(b'\0', str_off + n)
        names.append(d[str_off + n:end].decode())
    return names

def sleb(v):
    out = bytearray()
    while True:
        b = v & 0x7f
        v >>= 7
        if (v == 0 and not (b & 0x40)) or (v == -1 and (b & 0x40)):
            out.append(b)
            return bytes(out)
        out.append(b | 0x80)

def uleb(v):
    out = bytearray()
    while True:
        b = v & 0x7f
        v >>= 7
        if v:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)

def encode_crel(relocs):
    flag_bits = 2  # addend bit clear
    blob = bytearray(uleb(len(relocs) << 3))
    prev_off = prev_sym = prev_type = 0
    for off, sym, typ in sorted(relocs):
        delta = off - prev_off
        assert 0 <= delta < (0x80 >> flag_bits), 'large delta not implemented'
        flags = (1 if sym != prev_sym else 0) | (2 if typ != prev_type else 0)
        blob.append((delta << flag_bits) | flags)
        if flags & 1:
            blob += sleb(sym - prev_sym)
        if flags & 2:
            blob += sleb(typ - prev_type)
        prev_off, prev_sym, prev_type = off, sym, typ
    return bytes(blob)

classic_path, crel_path, out_path = sys.argv[1:4]
cd, csecs = read_elf32(classic_path)
kd, ksecs = read_elf32(crel_path)
cnames = symtab_names(cd, csecs)
knames = symtab_names(kd, ksecs)

for ks in ksecs:
    if not ks['name'].startswith('.crel.'):
        continue
    base = ks['name'][len('.crel'):]  # ".text" / ".data"
    cs = next(s for s in csecs if s['name'] == '.rel' + base)
    relocs = []
    for i in range(cs['size'] // 8):
        r_off, r_info = struct.unpack_from('<II', cd, cs['off'] + 8 * i)
        name = cnames[r_info >> 8]
        relocs.append((r_off, knames.index(name), r_info & 0xff))
    blob = encode_crel(relocs)
    assert len(blob) <= ks['size'], (ks['name'], len(blob), ks['size'])
    kd[ks['off']:ks['off'] + len(blob)] = blob
    struct.pack_into('<I', kd, ks['hdr_off'] + 20, len(blob))  # sh_size
    # carry the classic build's in-place addends into the patched sections
    tgt = next(s for s in ksecs if s['name'] == base)
    src = next(s for s in csecs if s['name'] == base)
    assert tgt['size'] == src['size']
    kd[tgt['off']:tgt['off'] + tgt['size']] = \
        cd[src['off']:src['off'] + src['size']]

open(out_path, 'wb').write(kd)
print('wrote', out_path)
