#!/usr/bin/env python3
"""Rebuild FAT disk fixtures with dosfstools; no tools are run by r2r tests."""
from pathlib import Path
import gzip
import json
import struct
import subprocess

HERE = Path(__file__).resolve().parent

def u16(data, off):
    return struct.unpack_from("<H", data, off)[0]

def u32(data, off):
    return struct.unpack_from("<I", data, off)[0]

def entry(name, cluster, size=0, attr=0x20, deleted=False):
    out = bytearray(32)
    out[:11] = name.encode("ascii").ljust(11, b" ")
    out[11] = attr
    out[12] = 0x18
    struct.pack_into("<H", out, 20, cluster >> 16)
    struct.pack_into("<H", out, 26, cluster & 65535)
    struct.pack_into("<I", out, 28, size)
    if deleted:
        out[0] = 0xe5
    return out

def lfn(name, short, deleted=False):
    encoded = name.encode("utf-16le") + b"\0\0"
    count = (len(encoded) + 25) // 26
    encoded = encoded.ljust(count * 26, b"\xff")
    checksum = 0
    for value in short.encode("ascii"):
        checksum = (((checksum >> 1) | (checksum << 7)) + value) & 255
    result = bytearray()
    for index in range(count, 0, -1):
        raw = bytearray(32)
        raw[0] = 0xe5 if deleted else index | (0x40 if index == count else 0)
        raw[11] = 15
        raw[13] = checksum
        part = encoded[(index - 1) * 26:index * 26]
        raw[1:11], raw[14:26], raw[28:32] = part[:10], part[10:22], part[22:]
        result.extend(raw)
    return result

def image(bits, sector, size):
    path = HERE / f"fat{bits}.img"
    with path.open("wb") as stream:
        stream.truncate(size)
    subprocess.run(["mkfs.fat", "-F", str(bits), "-S", str(sector), "-s", "1",
                    "-r", "128", "-i", "12345678", "-n", "R2FAT", str(path)], check=True)
    data = bytearray(path.read_bytes())
    reserved, fats, root_entries = u16(data, 14), data[16], u16(data, 17)
    fat_sectors = u16(data, 22) or u32(data, 36)
    sectors = u16(data, 19) or u32(data, 32)
    cluster_size = sector * data[13]
    root = (reserved + fats * fat_sectors) * sector
    first_data = root + ((root_entries * 32 + sector - 1) // sector) * sector
    root_cluster = u32(data, 44) if bits == 32 else 0
    root_at = first_data + (root_cluster - 2) * cluster_size if root_cluster else root
    count = (sectors - first_data // sector) // data[13]
    assert (12 if count < 4085 else 16 if count < 65525 else 32) == bits

    def address(cluster):
        return first_data + (cluster - 2) * cluster_size

    def fat_set(cluster, value, copy=None):
        for index in range(fats) if copy is None else (copy,):
            base = (reserved + index * fat_sectors) * sector
            off = base + (cluster + cluster // 2 if bits == 12 else cluster * (bits // 8))
            if bits == 12:
                current = u16(data, off)
                current = (current & 15) | (value << 4) if cluster & 1 else (current & 0xf000) | value
                struct.pack_into("<H", data, off, current)
            elif bits == 16:
                struct.pack_into("<H", data, off, value)
            else:
                struct.pack_into("<I", data, off, value)

    eof = (1 << bits) - 1 if bits != 32 else 0x0fffffff

    def chain(clusters, content):
        for i, cluster in enumerate(clusters):
            value = clusters[i + 1] if i + 1 < len(clusters) else eof
            fat_set(cluster, value | (0xa0000000 if bits == 32 else 0))
            part = content[i * cluster_size:(i + 1) * cluster_size]
            data[address(cluster):address(cluster) + len(part)] = part

    # Clear the formatter's volume-label entry; all listed entries are intentional.
    data[root_at:root_at + (cluster_size if bits == 32 else root_entries * 32)] = bytes(
        cluster_size if bits == 32 else root_entries * 32)
    records = bytearray()
    ids = {}

    def add(short, cluster, content=b"", attr=0x20, deleted=False, long_name=None, declared=None):
        if long_name:
            records.extend(lfn(long_name, short, deleted))
        ids[short.strip()] = root_at + len(records)
        records.extend(entry(short, cluster, len(content) if declared is None else declared, attr, deleted))

    live = f"FAT{bits} live\n".encode()
    chain([9], live)
    add("LIVE    TXT", 9, live)
    fragmented = b"A" * (cluster_size - 4) + b"END\n" + b"B" * 12 + b"TAIL\n"
    chain([3, 7], fragmented)
    add("FRAG    TXT", 3, fragmented)
    add("EMPTY   TXT", 0)
    chain([4], entry(".", 4, attr=0x10) + entry("..", root_cluster, attr=0x10)
          + entry("NESTED  TXT", 6, 7))
    chain([6], b"nested\n")
    add("SUBDIR     ", 4, attr=0x10)
    panda = b"unicode\n"
    chain([8], panda)
    add("PANDA~1 TXT", 8, panda, long_name="A long \U0001f43c name.txt")
    crossing = b"X" * cluster_size + b"cross!\n"
    chain([341, 342], crossing)
    add("CROSS   TXT", 341, crossing)

    # Simulate actual deletion: entry tombstones survive, allocation links do not.
    gone = b"G" * cluster_size + b"gone-tail\n"
    data[address(10):address(10) + len(gone)] = gone
    add("GONE    TXT", 10, gone, deleted=True)
    retained = b"C" * cluster_size + b"retained-tail\n"
    chain([12, 14], retained)
    add("CHAIN   TXT", 12, retained, deleted=True)
    data[address(15):address(15) + 96] = (
        entry(".", 15, attr=0x10) + entry("..", root_cluster, attr=0x10)
        + entry("CHILD   TXT", 16, 6, deleted=True))
    data[address(16):address(16) + 6] = b"child\n"
    add("OLDDIR     ", 15, attr=0x10, deleted=True)
    data[address(17):address(17) + 9] = b"lost-lfn\n"
    add("LOSTLO~1TXT", 17, b"lost-lfn\n", deleted=True, long_name="Lost long name.txt")
    chain([30, 31], b"orphan\n" + bytes(cluster_size * 2 - 7))
    data[address(40):address(40) + 16] = b"\x89PNG\r\n\x1a\nFREEPNG\n"
    if bits == 32:
        # The active FAT is copy 1; copy 0 retains a stale shorter file chain.
        struct.pack_into("<H", data, 40, 0x81)
        fat_set(3, eof, copy=0)
        fat_set(40, 0x50000000)
        for fsinfo in (1, 7):
            struct.pack_into("<I", data, fsinfo * sector + 488, 0xffffffff)
            struct.pack_into("<I", data, fsinfo * sector + 492, 0xffffffff)
    data[root_at:root_at + len(records)] = records
    if bits == 16:
        data[54:62] = b"        "
    path.with_suffix(".img.gz").write_bytes(gzip.compress(data, mtime=0))
    path.unlink()
    result = dict(bits=bits, sector=sector, cluster_size=cluster_size, clusters=count,
                  root=root_at, data=first_data, fat=reserved * sector,
                  fat_sectors=fat_sectors, ids=ids, size=len(data))
    if bits == 12:
        # Same source image in a disk with a nonzero partition offset.
        (HERE / "fat12-offset.img.gz").write_bytes(gzip.compress(bytes(4096) + data, mtime=0))
        for duplicate in (False, True):
            cycle = bytearray(data)
            cycle[root_at:root_at + root_entries * 32] = bytes(root_entries * 32)
            cycle[root_at:root_at + 32] = entry("DIR        ", 3, attr=0x10)
            directory = (entry("A          ", 3, attr=0x10) + entry("B          ", 3, attr=0x10)
                         if duplicate else entry("NOTE    TXT", 5, 15) + entry("INNER      ", 3, attr=0x10))
            cycle[address(3):address(3) + cluster_size] = directory.ljust(cluster_size, b"\0")
            cycle[address(5):address(5) + 15] = b"hello from fat\n"
            (HERE / ("fat12-tree-cycle.img.gz" if duplicate else "fat12-dir-cycle.img.gz")).write_bytes(gzip.compress(cycle, mtime=0))
    return result

if __name__ == "__main__":
    manifest = [image(12, 512, 1024 * 1024), image(16, 1024, 8 * 1024 * 1024),
                image(32, 512, 34 * 1024 * 1024)]
    (HERE / "layout.json").write_text(json.dumps(manifest, indent=2) + "\n")
