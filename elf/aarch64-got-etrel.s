# aarch64 ET_REL with :got:/:got_lo12: pairs for BOTH a defined-preemptible symbol
# (gdef) and an undefined one (gundef) - GOT reloc handling must distinguish them.
#   llvm-mc --triple=aarch64-linux-gnu --filetype=obj -o aarch64-got-etrel.o aarch64-got-etrel.s
	.text
	.globl	f
f:
	adrp	x0, :got:gdef
	ldr	x0, [x0, :got_lo12:gdef]
	adrp	x1, :got:gundef
	ldr	x1, [x1, :got_lo12:gundef]
	ret
	.data
	.globl	gdef
gdef:
	.quad	1
