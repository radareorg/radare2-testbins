	.syntax unified
	.arch armv7-a
	.thumb
	.text
	.globl f
	.thumb_func
f:
	.reloc ., R_ARM_THM_PC8, g
	ldr r0, [pc, #0]
	bx lr
	.reloc ., R_ARM_THM_ABS5, g
	ldr r0, [r1, #0]
	bx lr
	.reloc ., R_ARM_THM_JUMP6, g
	.inst.n 0xb100
	bx lr
	.globl g
	.thumb_func
g:
	bx lr
