# aarch64 ET_REL GOT relocs carrying a non-zero addend (gundef+8): for GOT
# relocs the addend selects the entry, it is not an offset from it, so every
# form below must resolve to the same GOT slot as a plain :got:gundef.
#   llvm-mc --triple=aarch64-linux-gnu --filetype=obj -o aarch64-got-etrel-addend.o aarch64-got-etrel-addend.s
	.text
	.globl	f
f:
	adrp	x1, :got:gundef+8
	ldr	x1, [x1, :got_lo12:gundef+8]
	adrp	x2, :got:gundef
	ldr	x2, [x2, :got_lo12:gundef]
	ldr	x3, :got:gundef+8
	ret
