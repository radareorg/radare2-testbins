# i386 CREL fixture, implicit-addend flavor (header addend bit clear, addends in place).
# llvm-mc --crel emits the explicit-addend flavor only, so build both and re-encode:
#   llvm-mc --triple=i386-linux-gnu --filetype=obj -o classic.o i386-crel.s
#   llvm-mc --triple=i386-linux-gnu --crel --filetype=obj -o container.o i386-crel.s
#   python3 mkcrel.py classic.o container.o i386-crel-implicit.o
# Two .crel.* sections on purpose: the second section's entries regress separately.
	.text
	.globl	f
f:
	call	g
	movl	v+4, %eax
	ret
	.globl	g
g:
	ret
	.data
	.globl	v
v:
	.long	0
	.long	0
	.long	v+8
	.long	f+2
