# x86-64 ET_REL with code-site relocs against SHN_COMMON and
# SHN_X86_64_LCOMMON symbols, next to the same relocs against an undefined
# symbol: a common symbol has no address until link time, so its relocs take
# a .got.r2 slot exactly as the import's do.
#   x86_64-linux-gnu-as -o x86_64-common-code.o x86_64-common-code.s
	.comm cbuf,8,8
	.largecomm lbuf,8,8
	.text
	.globl f
f:	mov cbuf(%rip), %rax
	call cbuf
	mov ext(%rip), %rax
	call ext
	ret
	.data
	.globl lptr
lptr:	.quad lbuf
