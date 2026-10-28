	.syntax unified
	.text
	.arm
	.globl caller
caller:
	bl thumbfn
	b thumbfn
	bx lr
	.thumb
	.globl thumbfn
	.type thumbfn,%function
	.thumb_func
thumbfn:
	bx lr
