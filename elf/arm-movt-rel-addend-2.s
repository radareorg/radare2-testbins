@ arm-mode rel object: movw/movt pairs with a positive absolute addend and
@ a pc-relative pair with a negative addend, both against the import ext.
	.syntax unified
	.arm
	.text
	.globl	f
	.type	f, %function
f:
	movw	r0, #:lower16:ext+8
	movt	r0, #:upper16:ext+8
	movw	r1, #:lower16:ext-16-.
	movt	r1, #:upper16:ext-16-.
	bx	lr
	.size	f, .-f
