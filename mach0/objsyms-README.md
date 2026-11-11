## objsyms-arm64.o, objsyms-armv7.o

Minimal Mach-O relocatable objects (MH_OBJECT) with a `__TEXT,__text` and a `__DATA,__data`
section and six symbols: local `_lf` and `_sdata`, global `_main`, absolute `_abs` (value 0x1000),
common `_common_var` (value is the size) and undefined `_ext`.

They are written by a script, not produced by a compiler. To rebuild them:

    python3 objsyms-gen.py <outdir>

Needs Python 3 only. The output is deterministic. Used by `test/db/formats/mach0/relocs` in radare2.
