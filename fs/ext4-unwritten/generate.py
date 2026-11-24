#!/usr/bin/env python3
"""Build a compact ext4 fixture whose unwritten extent covers stale data."""
import gzip
import os
from pathlib import Path
import subprocess
import tempfile

here = Path(__file__).resolve().parent
env = dict(os.environ, E2FSPROGS_FAKE_TIME='1700000000')
with tempfile.TemporaryDirectory() as directory:
    temporary = Path(directory)
    image = temporary / 'unwritten.img'
    image.write_bytes(bytes(512 * 1024))
    subprocess.run(['mke2fs', '-q', '-F', '-t', 'ext4', '-b', '1024',
                    '-I', '128', '-N', '64', '-O', '^has_journal,^resize_inode', '-m', '0',
                    '-E', 'hash_seed=12345678-1234-5678-1234-567812345678',
                    '-U', '12345678-1234-5678-1234-567812345678', str(image)], check=True, env=env)
    live = temporary / 'live'
    live.write_bytes(b'Live ext4 file\n')
    stale = temporary / 'stale'
    stale.write_bytes(b'Stale secret\n' * 315)
    empty = temporary / 'empty'
    empty.write_bytes(b'')
    commands = temporary / 'commands'
    commands.write_text(f'write {live} /live\nwrite {stale} /old\nrm /old\n'
                        f'write {empty} /prealloc\nfallocate /prealloc 0 3\nsif /prealloc size 4096\n')
    subprocess.run(['debugfs', '-w', '-f', str(commands), str(image)], check=True, env=env)
    (here / 'unwritten.img.gz').write_bytes(gzip.compress(image.read_bytes(), mtime=0))
