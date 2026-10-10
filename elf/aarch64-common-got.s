# aarch64 ET_REL with GOT relocs against an SHN_COMMON symbol, next to the
# same pair against an undefined symbol: both load their address from a
# .got.r2 slot.
#   /usr/lib/llvm-21/bin/llvm-mc -triple=aarch64-linux-gnu -filetype=obj \
#       -o aarch64-common-got.o aarch64-common-got.s
	.comm cbuf,8,8
	.text
	.globl f
f:	adrp x0, :got:cbuf
	ldr x0, [x0, :got_lo12:cbuf]
	adrp x1, :got:ext
	ldr x1, [x1, :got_lo12:ext]
	ret
