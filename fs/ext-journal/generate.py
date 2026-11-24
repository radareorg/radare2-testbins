#!/usr/bin/env python3
"""Build compact ext3/ext4 images containing retained committed journal records."""
from pathlib import Path
import gzip
import json
import re
import struct
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
MAGIC = 0xc03b3998
BLOCK = 1024
MANIFEST = {}

def crc32c(data):
    crc = 0xffffffff
    for value in data:
        crc ^= value
        for _ in range(8):
            crc = (crc >> 1) ^ (0x82f63b78 if crc & 1 else 0)
    return crc

def crc32be(data, crc=0xffffffff):
    for value in data:
        crc ^= value << 24
        for _ in range(8):
            crc = ((crc << 1) ^ (0x04c11db7 if crc & 0x80000000 else 0)) & 0xffffffff
    return crc

def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout

def make(format_name, ext4=False, checksum=0):
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        path = temp / 'image'
        path.write_bytes(bytes(4 * 1024 * 1024))
        features = 'has_journal,filetype,extent,64bit,flex_bg,metadata_csum' if ext4 else 'has_journal,filetype'
        run('mke2fs', '-q', '-F', '-t', 'ext4' if ext4 else 'ext3', '-b', str(BLOCK),
            '-I', '256' if ext4 else '128', '-N', '64', '-O', 'none,' + features,
            '-J', 'size=1', '-m', '0', '-U', '12345678-1234-5678-1234-567812345678', str(path))
        live = temp / 'live'
        live.write_bytes(b'Live journal file\n')
        victim = temp / 'victim'
        victim.write_bytes(b'Deleted through the journal\n')
        commands = temp / 'commands'
        commands.write_text(f'write {live} /live\nwrite {victim} /victim\n')
        run('debugfs', '-w', '-f', str(commands), str(path))
        old = bytearray(path.read_bytes())
        victim_block = int(run('debugfs', '-R', 'bmap /victim 0', str(path)).strip())
        inode_size = struct.unpack_from('<H', old, 1024 + 88)[0]
        inode_table = struct.unpack_from('<I', old, 2048 + 8)[0]
        inode_offset = inode_table * BLOCK + 12 * inode_size
        inode_block = inode_offset // BLOCK
        run('debugfs', '-w', '-R', 'rm /victim', str(path))
        run('debugfs', '-w', '-R', 'sif <13> size 0', str(path))
        image = bytearray(path.read_bytes())
        commands.write_text(''.join(f'bmap <8> {i}\n' for i in range(32)))
        mapping = [int(line) for line in run('debugfs', '-f', str(commands), str(path)).splitlines() if re.fullmatch(r'\d+', line)]
        assert len(mapping) == 32
        mapping = dict(enumerate(mapping))
        super_offset = mapping[0] * BLOCK
        journal_super = bytearray(image[super_offset:super_offset + BLOCK])
        uuid = bytes(journal_super[48:64])
        length = struct.unpack_from('>I', journal_super, 16)[0]
        for number in (length - 2, length - 1):
            mapping[number] = int(run('debugfs', '-R', f'bmap <8> {number}', str(path)).strip())
        incompat = 1 | (2 if ext4 else 0) | ({0: 0, 1: 0, 2: 8, 3: 16}[checksum])
        struct.pack_into('>III', journal_super, 36, int(checksum == 1), incompat, 0)
        struct.pack_into('>II', journal_super, 24, 200, 0)
        journal_super[80] = 4 if checksum >= 2 else 0
        struct.pack_into('>I', journal_super, 252, 0)
        if checksum >= 2:
            struct.pack_into('>I', journal_super, 252, crc32c(journal_super))
        image[super_offset:super_offset + BLOCK] = journal_super

        base_image = bytearray(image)

        def step(number):
            return number + 1 if number + 1 < length else 1

        def store(number, data):
            image[mapping[number] * BLOCK:(mapping[number] + 1) * BLOCK] = data

        def metadata(block_type, sequence):
            data = bytearray(BLOCK)
            struct.pack_into('>III', data, 0, MAGIC, block_type, sequence)
            return data

        def tail(data, commit=False):
            if checksum >= 2:
                offset = 16 if commit else BLOCK - 4
                struct.pack_into('>I', data, offset, 0)
                struct.pack_into('>I', data, offset, crc32c(uuid + data))
            return data

        def transaction(number, sequence, target, payload, escape=False, revoke=False, commit=True):
            data = bytearray(payload)
            flags = 8 | int(escape)
            if escape:
                struct.pack_into('>I', data, 0, 0)
            csum = crc32c(uuid + struct.pack('>I', sequence) + data)
            descriptor = metadata(1, sequence)
            if checksum == 3:
                tag = struct.pack('>IIII', target & 0xffffffff, flags, target >> 32, csum)
            else:
                tag = struct.pack('>IHH', target & 0xffffffff, csum & 0xffff if checksum == 2 else 0, flags)
                if ext4:
                    tag += struct.pack('>I', target >> 32)
                if checksum == 2:
                    tag += bytes(2)
            descriptor[12:12 + len(tag) + 16] = tag + uuid
            tail(descriptor)
            store(number, descriptor)
            store(step(number), data)
            cursor = step(step(number))
            if revoke:
                rev = metadata(5, sequence)
                width = 8 if ext4 else 4
                struct.pack_into('>I', rev, 12, 16 + width)
                struct.pack_into('>Q' if ext4 else '>I', rev, 16, target)
                store(cursor, tail(rev))
                cursor = step(cursor)
            if commit:
                end = metadata(2, sequence)
                if checksum == 1:
                    end[12:14] = bytes((1, 4))
                    struct.pack_into('>I', end, 16, crc32be(data, crc32be(descriptor)))
                store(cursor, tail(end, commit=True))
            return step(cursor)

        cursor = transaction(1, 99, victim_block, old[victim_block * BLOCK:(victim_block + 1) * BLOCK])
        cursor = transaction(cursor, 100, inode_block, old[inode_block * BLOCK:(inode_block + 1) * BLOCK])
        payload = bytearray(BLOCK)
        payload[:12] = struct.pack('>I', MAGIC) + b'ESCAPED\n'
        cursor = transaction(cursor, 101, 3500, payload, escape=True)
        payload = bytearray(BLOCK)
        payload[:8] = b'REVOKED\n'
        cursor = transaction(cursor, 102, 3501, payload, revoke=True)
        transaction(cursor, 103, 3502, bytearray(BLOCK), commit=False)
        MANIFEST[format_name] = {'journal': mapping, 'inode_offset': inode_offset, 'inode_block': inode_block,
                                 'victim_block': victim_block, 'inode_size': inode_size, 'checksum': checksum,
                                 'ext4': ext4}
        destination = HERE / (format_name + '.img.gz')
        destination.write_bytes(gzip.compress(image, mtime=0))
        print(destination.name, destination.stat().st_size, 'bytes; inode 13 in block', inode_block)
        if format_name == 'ext4-v3':
            image = base_image
            payload = bytearray(BLOCK)
            payload[:12] = struct.pack('>I', MAGIC) + b'WRAPPED\n'
            transaction(length - 2, 0xffffffff, 3500, payload, escape=True)
            (HERE / 'ext4-wrap.img.gz').write_bytes(gzip.compress(image, mtime=0))
            MANIFEST['ext4-wrap'] = dict(MANIFEST[format_name])
            image = bytearray(base_image)
            transaction(1, 0xffffffff, 3500, payload, escape=True)
            rev = metadata(5, 0xffffffff)
            struct.pack_into('>IQ', rev, 12, 24, 3500)
            store(length - 1, tail(rev))
            (HERE / 'ext4-wrap-revoke.img.gz').write_bytes(gzip.compress(image, mtime=0))
            MANIFEST['ext4-wrap-revoke'] = dict(MANIFEST[format_name])

make('ext3')
make('ext3-crc', checksum=1)
make('ext4-v2', ext4=True, checksum=2)
make('ext4-v3', ext4=True, checksum=3)

(HERE / 'manifest.json').write_text(json.dumps(MANIFEST, indent=2) + '\n')
