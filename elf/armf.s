	.syntax unified
	.text
	.arm
	.globl af
	.type af,%function
af:
	bx lr
	.thumb
	.globl thf
	.type thf,%function
	.thumb_func
thf:
	movw r0, #:lower16:af
	movt r0, #:upper16:af
	bx lr
