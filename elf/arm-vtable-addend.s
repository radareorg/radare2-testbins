@ arm EABI shared object, rel: each word's addend is its in-place value.
@ ti is a C++ typeinfo word, class_type_info's vtable + 8; ext_a..ext_c
@ are plain import words, so ti + 8 names ext_b's slot unless the slot
@ for class_type_info spans its addend.
	.syntax unified
	.arm
	.text
	.globl	f
	.type	f, %function
f:
	bx	lr
	.size	f, .-f

	.data
	.globl	ti
	.type	ti, %object
	.p2align 2
ti:
	.long	_ZTVN10__cxxabiv117__class_type_infoE+8
	.long	ext_a
	.long	ext_b
	.long	ext_c
	.size	ti, .-ti
