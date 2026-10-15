	.text
	.globl f
f:	ret
	.section .rodata
msg:	.asciz "hello_from_high_memory"
	.data
	.p2align 2
tab:	.word msg
	.word tab
