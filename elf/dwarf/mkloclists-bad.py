#!/usr/bin/env python3
# Derives the malformed and edge-case .debug_loclists fixtures from
# loclists-x64-clang and loclists-aarch64-gcc. Offsets are into the file;
# every patch asserts the bytes it replaces so a regenerated input is noticed.
import shutil

CLANG = "loclists-x64-clang"
GCC = "loclists-aarch64-gcc"
CLANG_LOCLISTS = 0x27a  # .debug_loclists file offset
CLANG_INFO = 0x40b  # .debug_info file offset
GCC_LOCLISTS = 0x828


def patch(data, offset, old, new):
    assert data[offset:offset + len(old)] == bytes(old), hex(offset)
    assert len(old) == len(new)
    data[offset:offset + len(new)] = bytes(new)


def derive(src, dst, patches):
    with open(src, "rb") as f:
        data = bytearray(f.read())
    for offset, old, new in patches:
        patch(data, offset, old, new)
    with open(dst, "wb") as f:
        f.write(data)
    shutil.copymode(src, dst)


L = CLANG_LOCLISTS
derive(CLANG, "loclists-x64-semantics", [
    # a: the second range's entry_value expression becomes DW_OP_fbreg 16
    (L + 0x2d, [0xa3, 0x01, 0x55, 0x9f], [0x91, 0x10, 0x96, 0x96]),
    # b: a default location (rbx) between bounded ranges in rdx, then an empty range
    (L + 0x32, [0x04, 0x00, 0x0f, 0x01, 0x54, 0x04, 0x0f, 0x11, 0x01, 0x53,
                0x04, 0x11, 0x21, 0x04, 0xa3, 0x01, 0x54, 0x9f],
               [0x04, 0x00, 0x0f, 0x01, 0x51, 0x05, 0x01, 0x53,
                0x04, 0x0f, 0x21, 0x01, 0x51, 0x04, 0x21, 0x21, 0x01, 0x51]),
    # x: the same range as DW_LLE_startx_length through .debug_addr entry 2
    (L + 0x45, [0x04, 0x08, 0x20, 0x01, 0x56], [0x03, 0x02, 0x08, 0x01, 0x56]),
    # y: startx_length with an index past the .debug_addr table
    (L + 0x4b, [0x04, 0x0f, 0x18, 0x01, 0x50], [0x03, 0x7f, 0x18, 0x01, 0x50]),
    # z: only a default location (rbx)
    (L + 0x51, [0x04, 0x11, 0x1f, 0x01, 0x53], [0x05, 0x03, 0x53, 0x96, 0x96]),
    # _start's r: the rcx range grows past the end of the function
    (L + 0x7a, [0x04, 0x18, 0x1a, 0x01, 0x52], [0x04, 0x18, 0x7f, 0x01, 0x52]),
])
derive(CLANG, "loclists-x64-bad-entries", [
    # b: the second range reversed, 0x11..0xf
    (L + 0x38, [0x0f, 0x11], [0x11, 0x0f]),
    # x: its only range reversed, 0x20..0x8
    (L + 0x46, [0x08, 0x20], [0x20, 0x08]),
    # z: the end-of-list marker replaced by an unknown entry kind
    (L + 0x56, [0x00], [0x96]),
])
derive(CLANG, "loclists-x64-bad-contribution", [
    # the first contribution's length cut from 0x61 to 0x4f: it now ends inside z's list
    (L + 0x0, [0x61], [0x4f]),
])
derive(CLANG, "loclists-x64-bad-index", [
    # x's DW_FORM_loclistx index 2 becomes 9, past the 6-entry offset table
    (CLANG_INFO + 0x49, [0x02], [0x09]),
])
derive(GCC, "loclists-aarch64-bad-base", [
    # the list at 0x44: base 0xfffffffffffffff8 and a first pair 0x8..0xc, so
    # both sums wrap to a consistent range 0x0..0x4
    (GCC_LOCLISTS + 0x45, [0xc0, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00],
                          [0xf8, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff]),
    (GCC_LOCLISTS + 0x4d, [0x04, 0x00, 0x04], [0x04, 0x08, 0x0c]),
])
