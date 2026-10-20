// R_AARCH64_PREL64 and R_AARCH64_MOVW_UABS_G0..G3 against a defined local symbol, for radare2's `ir` listing of
// an ET_REL object (the rows must be listed, not dropped).
// Build: llvm-mc -triple=aarch64-linux-gnu -filetype=obj aarch64-prel64-movw.s -o aarch64-prel64-movw.o
	.text
	.globl	f
f:	ret
	movz	x0, #:abs_g0:f
	movk	x0, #:abs_g1_nc:f
	movk	x0, #:abs_g2_nc:f
	movk	x0, #:abs_g3:f
	.data
p:	.xword	f - p
