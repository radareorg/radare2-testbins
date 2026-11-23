# FAT reader and forensic fixtures

Run `python3 generate.py` with dosfstools installed to rebuild these images.
The stored fixtures total about 50 KiB. FAT32 requires a logical volume of at
least roughly 32 MiB, but its zero-filled free space compresses to a few tens of KiB.
Tests decompress in memory and never create temporary disk images.

The generator starts with `mkfs.fat` volumes and adds known directory entries,
file contents, fragmented chains and deletion remnants. Tests only read the
stored gzip images through radare2's `gzip://` IO plugin; they do not invoke
the generator or external filesystem tools.

- `fat12.img.gz`: 512-byte sectors, fixed root directory, fragmented files,
  a FAT12 entry crossing a sector boundary, empty files and UTF-16 VFAT names.
- `fat16.img.gz`: 1024-byte sectors and a blank advisory filesystem-type string.
- `fat32.img.gz`: 512-byte sectors, root cluster 2, active FAT copy 1, a stale
  shorter chain in inactive copy 0, and nonzero reserved high FAT-entry bits.
- `fat12-offset.img.gz`: the FAT12 volume preceded by 4096 bytes.
- `fat12-dir-cycle.img.gz`: a directory referring to itself through one child.
- `fat12-tree-cycle.img.gz`: a directory referring to itself through two children.

`layout.json` records geometry and short-entry byte offsets. IDs are relative
to the volume, while the offset image adds its 4096-byte prefix to disk offsets.

All three main volumes contain deleted entries with cleared FAT chains,
a deleted entry whose fragmented chain survives, a deleted directory, deleted
VFAT fragments, an allocated orphan chain at clusters 30 and 31, and a PNG
signature in free cluster 40. These remnants are intentional: fsck can report
lost clusters and the missing root volume-label entry. Do not repair the images.
