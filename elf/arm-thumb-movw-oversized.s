@ thumb rel object: a movw/movt pair against ext with an addend past any
@ slot r2 reserves, then an arm-mode pair at ext and an arm movw at ext-4.
	.syntax unified
	.text
	.thumb
	.globl	f
	.type	f, %function
	.thumb_func
f:
	movw	r0, #:lower16:ext+0x2000
	movt	r0, #:upper16:ext+0x2000
	bx	lr
	.arm
	.globl	g
	.type	g, %function
g:
	movw	r1, #:lower16:ext
	movt	r1, #:upper16:ext
	bx	lr
	.globl	h
	.type	h, %function
h:
	movw	r2, #:lower16:ext-4
	bx	lr
