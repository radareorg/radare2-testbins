# NTFS forensic fixture

`recovery.img.gz` is about 129 KiB compressed and expands to an 8 MiB NTFS
volume with 512-byte clusters, 512-byte sectors and 1024-byte MFT records.
The standard Unicode `$UpCase` table accounts for most of the compressed size.
No expanded image is checked in. Regenerate with `python3 generate.py` using
ntfs-3g's `mkntfs` and `ntfscp` tools.

- MFT 64, `/live.txt`: resident `Live NTFS file\n`.
- MFT 65, deleted `/vanished.bin`: `Recover NTFS data\n` repeated 1024 times.
  Three physical runs include a backward LCN delta. The in-use flag, MFT bitmap
  bit and data cluster bits are clear while the file's metadata is retained.
- MFT 66, deleted `/inline.txt`: resident `Resident NTFS recovery\n` repeated
  sixteen times. Its data crosses a sector update-sequence fixup boundary.
- MFT 67, `/sparse.bin`: logical size 4294967808, with `A` at the start and
  `Z` at offset 4294967296. Each data block is 512 bytes; the intervening
  mapping is sparse.
- MFT 68, `/unwritten.bin`: a 1024-byte nonresident file initialized only through
  byte 17. The rest of its physical data contains `X` and must read as zero.

The generator applies explicit metadata changes after creating the volume;
it does not simulate Windows journal replay. `manifest.json` describes MFT
locations and mapping pairs for corruption and reuse tests.
