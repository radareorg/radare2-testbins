	.text
	.globl foo
	.type foo,%function
foo:
	bti c
	bl bar
	bl baz
	bl qux
	ret
	.section .note.gnu.property,"a"
	.p2align 3
	.long 4
	.long 16
	.long 5
	.asciz "GNU"
	.long 0xc0000000
	.long 4
	.long 1
	.long 0
