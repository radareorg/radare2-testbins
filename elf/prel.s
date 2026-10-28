	.syntax unified
	.thumb
	.text
	.globl f
	.type f,%function
f:
	movw r0, :lower16:(target - .)
	movt r0, :upper16:(target - .)
	bx lr
	.data
	.globl target
target:
	.word 0x11223344
