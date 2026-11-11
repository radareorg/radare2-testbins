# x86-64 ET_REL with common symbols of unsupported size and alignment:
# over 1MB, over 1MB aligned, and a size above 32 bits.
#   gcc -c -o x86_64-common-oversize.o x86_64-common-oversize.s
	.comm	fits,0x80000,8
	.comm	big2m,0x200000,8
	.comm	align2m,8,0x200000
	.comm	wrap32,0x100000010,8
	.text
	.globl	f
f:
	mov	fits(%rip), %eax
	mov	big2m(%rip), %eax
	mov	align2m(%rip), %eax
	mov	wrap32(%rip), %eax
	ret
