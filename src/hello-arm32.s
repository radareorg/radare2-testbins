	.syntax unified
	.arch armv7-a
	.fpu vfpv3-d16
	.file	"a.c"
	.section	.rodata
	.align	4
.LC0:
	.ascii	"Hello World\000"
	.text
	.align	4
	.global	foo
	.type	foo, %function
foo:
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 1, uses_anonymous_args = 0
	push	{r7, lr}
	add	r7, sp, #0
	movw	r0, #:lower16:.LC0
	movt	r0, #:upper16:.LC0
	bl	puts
	movs	r3, #0
	mov	r0, r3
	bl	exit
	pop	{r7, pc}
	.size	foo, .-foo
	.align	4
	.global	main
	.type	main, %function
main:
_start:
	@ args = 0, pretend = 0, frame = 0
	@ frame_needed = 1, uses_anonymous_args = 0
	bl	foo
	.size	main, .-main
