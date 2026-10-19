	.section .data
	.globl ptr
ptr:	.quad ext_fn
	.section .text.foo,"ax",@progbits
	.globl foo
	.type foo,@function
foo:	call ext_fn
	ret
