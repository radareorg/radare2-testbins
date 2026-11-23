#!/usr/bin/env python3
"""Build a compact classic ext2 recovery fixture using e2fsprogs."""
import gzip
from pathlib import Path
import subprocess
import tempfile

here = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as directory:
    temporary = Path(directory)
    image = temporary / 'recovery.img'
    image.write_bytes(bytes(512 * 1024))
    subprocess.run(['mke2fs', '-q', '-F', '-t', 'ext2', '-b', '1024',
                    '-I', '128', '-N', '64', '-O', 'none', '-m', '0',
                    '-U', '12345678-1234-5678-1234-567812345678', str(image)], check=True)
    live = temporary / 'live'
    live.write_bytes(b'Live ext2 file\n')
    deleted = temporary / 'deleted'
    deleted.write_bytes(b'Recover ext2 data\n' * 1024)
    commands = temporary / 'commands'
    commands.write_text(f'write {live} /live\nwrite {deleted} /vanished\nsymlink /link live\nrm /vanished\n')
    subprocess.run(['debugfs', '-w', '-f', str(commands), str(image)], check=True)
    (here / 'recovery.img.gz').write_bytes(gzip.compress(image.read_bytes(), mtime=0))
