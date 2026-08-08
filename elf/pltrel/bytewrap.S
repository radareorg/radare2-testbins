/* An 8 bit write to an argument register still supplies that argument, so this
   wrapper is not transparent either. Hand written because compilers widen it. */
	.text
	.globl	byteleaf
	.type	byteleaf,@function
byteleaf:
	leal	1(%rdi), %eax
	ret
	.size	byteleaf, .-byteleaf

	.globl	bytewrap
	.hidden	bytewrap
	.type	bytewrap,@function
bytewrap:
	movb	$1, %dil
	jmp	byteleaf@PLT
	.size	bytewrap, .-bytewrap

	.globl	top_byte
	.type	top_byte,@function
top_byte:
	pushq	%rax
	call	bytewrap
	incl	%eax
	popq	%rcx
	ret
	.size	top_byte, .-top_byte
