// R_AARCH64_MOVW_UABS_G0_NC/G1/G2 (listed) and R_AARCH64_MOVW_SABS_G0 (unsupported, omitted) for radare2's `ir` on ET_REL
	.text
	.globl	f
f:	ret
	movk	x0, #:abs_g0_nc:f
	movz	x0, #:abs_g1:f
	movz	x0, #:abs_g2:f
	movz	x0, #:abs_g0_s:f
