#!/usr/bin/env python3
# Writes an x86-64 ELF whose DWARF holds two function pointer typedefs that
# cost an exponential number of renders when a parameter type is rendered
# again for every reference to it:
#   cycle: a pointer to a subroutine type whose three parameters are that
#          same pointer
#   chain: CHAIN pointers to subroutine types whose two parameters are the
#          next pointer, the last one taking two ints
# usage: mkdwarffanout.py [out]   (default: dwarf_subroutine_type_fanout)
import struct
import sys

CHAIN = 29

DW_TAG_compile_unit = 0x11
DW_TAG_base_type = 0x24
DW_TAG_pointer_type = 0x0f
DW_TAG_subroutine_type = 0x15
DW_TAG_formal_parameter = 0x05
DW_TAG_typedef = 0x16
DW_AT_name = 0x03
DW_AT_byte_size = 0x0b
DW_AT_language = 0x13
DW_AT_prototyped = 0x27
DW_AT_encoding = 0x3e
DW_AT_type = 0x49
DW_FORM_data1 = 0x0b
DW_FORM_string = 0x08
DW_FORM_ref4 = 0x13
DW_FORM_flag_present = 0x19
DW_LANG_C99 = 0x0c
DW_ATE_signed = 0x05

ABBREVS = [
    (DW_TAG_compile_unit, 1, [(DW_AT_name, DW_FORM_string), (DW_AT_language, DW_FORM_data1)]),
    (DW_TAG_base_type, 0, [(DW_AT_name, DW_FORM_string), (DW_AT_byte_size, DW_FORM_data1), (DW_AT_encoding, DW_FORM_data1)]),
    (DW_TAG_pointer_type, 0, [(DW_AT_byte_size, DW_FORM_data1), (DW_AT_type, DW_FORM_ref4)]),
    (DW_TAG_subroutine_type, 1, [(DW_AT_prototyped, DW_FORM_flag_present)]),
    (DW_TAG_formal_parameter, 0, [(DW_AT_type, DW_FORM_ref4)]),
    (DW_TAG_typedef, 0, [(DW_AT_name, DW_FORM_string), (DW_AT_type, DW_FORM_ref4)]),
]
CU, BASE, PTR, SUB, PARAM, TYPEDEF = range(1, len(ABBREVS) + 1)
CU_HEADER_SIZE = 11


def uleb(v):
    out = b""
    while True:
        b = v & 0x7f
        v >>= 7
        if not v:
            return out + bytes([b])
        out += bytes([b | 0x80])


def debug_abbrev():
    out = b""
    for code, (tag, children, attrs) in enumerate(ABBREVS, 1):
        out += uleb(code) + uleb(tag) + bytes([children])
        for at, form in attrs:
            out += uleb(at) + uleb(form)
        out += b"\0\0"
    return out + b"\0"


def ref(off):
    return struct.pack("<I", off)


def function_pointer(at, params):
    # pointer at `at`, its subroutine type right after it
    sub = at + 6
    die = bytes([PTR, 8]) + ref(sub)
    die += bytes([SUB]) + b"".join(bytes([PARAM]) + ref(p) for p in params) + b"\0"
    return die


def debug_info():
    body = bytes([CU]) + b"fanout.c\0" + bytes([DW_LANG_C99])
    int_off = CU_HEADER_SIZE + len(body)
    body += bytes([BASE]) + b"int\0" + bytes([4, DW_ATE_signed])
    cycle = CU_HEADER_SIZE + len(body)
    body += function_pointer(cycle, [cycle] * 3)
    body += bytes([TYPEDEF]) + b"cycle\0" + ref(cycle)
    first = CU_HEADER_SIZE + len(body)
    size = len(function_pointer(0, [0, 0]))
    for i in range(CHAIN):
        at = first + i * size
        nxt = at + size if i + 1 < CHAIN else int_off
        body += function_pointer(at, [nxt, nxt])
    body += bytes([TYPEDEF]) + b"chain\0" + ref(first)
    body += b"\0"
    header = struct.pack("<HIB", 4, 0, 8)
    return struct.pack("<I", len(header) + len(body)) + header + body


def elf(sections, text_addr=0x400078):
    secs = [(".text", b"\xc3")] + sections
    shstr = b"\0"
    name_off = {}
    for name, _ in secs + [(".shstrtab", b"")]:
        name_off[name] = len(shstr)
        shstr += name.encode() + b"\0"
    secs.append((".shstrtab", shstr))
    ehsize, phsize, shsize = 64, 56, 64
    off = ehsize + phsize
    offs = []
    for _, data in secs:
        offs.append(off)
        off += len(data)
    eh = b"\x7fELF" + bytes([2, 1, 1, 0]) + b"\0" * 8
    eh += struct.pack("<HHIQQQIHHHHHH", 2, 0x3e, 1, text_addr, ehsize, off, 0,
        ehsize, phsize, 1, shsize, len(secs) + 1, len(secs))
    ph = struct.pack("<IIQQQQQQ", 1, 5, 0, 0x400000, 0x400000,
        ehsize + phsize + 1, ehsize + phsize + 1, 0x1000)
    sh = b"\0" * shsize
    for (name, data), o in zip(secs, offs):
        kind, flags, addr = (1, 6, text_addr) if name == ".text" else (3 if name == ".shstrtab" else 1, 0, 0)
        sh += struct.pack("<IIQQQQIIQQ", name_off[name], kind, flags, addr, o, len(data), 0, 0, 1, 0)
    return eh + ph + b"".join(data for _, data in secs) + sh


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "dwarf_subroutine_type_fanout"
    data = elf([(".debug_abbrev", debug_abbrev()), (".debug_info", debug_info())])
    with open(out, "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
