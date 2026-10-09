# aarch64 ET_DYN linked at a non-zero image base with its RELATIVE relocs packed
# as DT_RELR, so each slot's own word is the addend.
#   /usr/lib/llvm-21/bin/llvm-mc -triple=aarch64-linux-gnu -filetype=obj \
#       -o aarch64-relr-linkbase.o aarch64-relr-linkbase.s
#   ld.lld-21 -shared -Bsymbolic -z pack-relative-relocs --image-base=0x40000 \
#       -o aarch64-relr-linkbase.so aarch64-relr-linkbase.o
	.text
	.globl f
f:	ret
	.data
	.p2align 3
	.globl tab
tab:	.quad f
	.quad tab+8
	.quad tab+16
	.quad f+4
	.quad 0x1234
