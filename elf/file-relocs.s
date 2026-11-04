	.text
	.globl _start
	.type _start, @function
_start:
	movl x(%rip), %eax
	call helper
	ret
	.globl helper
	.type helper, @function
helper:
	ret
	.data
	.globl x
	.type x, @object
x:
	.long 3
