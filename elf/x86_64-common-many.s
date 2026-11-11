# x86-64 ET_REL with common symbols whose total storage exceeds the
# .got.r2 growth budget: the ones that do not fit stay unpatched.
#   gcc -c -o x86_64-common-many.o x86_64-common-many.s
	.comm	c0,0x20000,0x1000
	.comm	c1,0x20000,0x1000
	.comm	c2,0x20000,0x1000
	.comm	c3,0x20000,0x1000
	.comm	c4,0x20000,0x1000
	.comm	c5,0x20000,0x1000
	.comm	c6,0x20000,0x1000
	.comm	c7,0x20000,0x1000
	.comm	c8,0x20000,0x1000
	.comm	huge,0x40,0x100000
	.text
	.globl	f
f:
	mov	c0(%rip), %eax
	mov	c1(%rip), %eax
	mov	c2(%rip), %eax
	mov	c3(%rip), %eax
	mov	c4(%rip), %eax
	mov	c5(%rip), %eax
	mov	c6(%rip), %eax
	mov	c7(%rip), %eax
	mov	c8(%rip), %eax
	mov	huge(%rip), %eax
	ret
