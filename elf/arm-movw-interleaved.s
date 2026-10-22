@ rel object: interleaved movw/movt pairs against ext, one pair with an
@ addend past any slot r2 reserves and one at ext, in arm and thumb mode.
	.syntax unified
	.text
	.arm
	.globl	f
	.type	f, %function
f:
	movw	r0, #:lower16:ext+0x2000
	movw	r1, #:lower16:ext
	movt	r0, #:upper16:ext+0x2000
	movt	r1, #:upper16:ext
	bx	lr
	.thumb
	.globl	g
	.type	g, %function
	.thumb_func
g:
	movw	r2, #:lower16:ext+0x2000
	movw	r3, #:lower16:ext
	movt	r2, #:upper16:ext+0x2000
	movt	r3, #:upper16:ext
	bx	lr
