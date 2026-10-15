	.syntax unified
	.thumb
	.text
	.globl f
	.thumb_func
f:
	b.n g
	beq.n g
	bx lr
	.globl g
	.thumb_func
g:
	bx lr
