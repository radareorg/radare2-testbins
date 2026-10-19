// ARM-mode MOVW/MOVT REL relocations (addend in the instruction's imm16), ABS and PREL, zero, positive and negative.
// Build: arm-linux-gnueabihf-as -march=armv7-a arm-movt-prel.s -o arm-movt-prel.o
	.syntax	unified
	.arm
	.text
	.globl	f
f:
	movw	r0, #:lower16:ext + 8
	movt	r0, #:upper16:ext + 8
	movw	r1, #:lower16:ext - .
	movt	r1, #:upper16:ext - .
	movw	r2, #:lower16:ext + 16 - .
	movt	r2, #:upper16:ext + 16 - .
	movw	r3, #:lower16:ext - 4 - .
	movt	r3, #:upper16:ext - 4 - .
	bx	lr
