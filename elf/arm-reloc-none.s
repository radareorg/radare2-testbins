	.syntax unified
	.arm
	.text
	.globl f
	.type f,%function
f:
	.reloc ., R_ARM_NONE, keep
	bx lr
	.reloc ., R_ARM_GOT_PREL, keep
	mov r0, r1
keep:	.word 0
