#!/usr/bin/env python3
"""Generate a small compressed ext4 fixture with a retained deleted extent tree."""
import gzip
from pathlib import Path
import subprocess
import tempfile

here = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as directory:
    temporary = Path(directory)
    image = temporary / 'recovery.img'
    image.write_bytes(bytes(8 * 1024 * 1024))
    subprocess.run(['mke2fs', '-q', '-F', '-t', 'ext4', '-b', '1024', '-g', '1024',
                    '-G', '4', '-I', '256', '-N', '128', '-m', '0',
                    '-O', 'extent,64bit,flex_bg,metadata_csum',
                    '-E', 'lazy_itable_init=1', '-U', '12345678-1234-5678-1234-567812345678', str(image)], check=True)
    live = temporary / 'live'
    live.write_bytes(b'Live ext4 file\n')
    deleted = temporary / 'deleted'
    deleted.write_bytes(b''.join(bytes([65 + i]) * 1024 if not i % 2 else bytes(1024) for i in range(13)))
    commands = temporary / 'commands'
    commands.write_text(f'write {live} /live\nwrite {deleted} /vanished\nwrite {live} /unwritten\nfallocate /unwritten 1 3\nset_inode_field /unwritten size 4096\nsymlink /link live\nrm /vanished\nstat <13>\n')
    subprocess.run(['debugfs', '-w', '-f', str(commands), str(image)], check=True)
    (here / 'recovery.img.gz').write_bytes(gzip.compress(image.read_bytes(), mtime=0))
