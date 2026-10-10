# x86-64 ET_REL with a reloc against an SHN_COMMON symbol, which has no
# address until link time: the relocs stay unresolved, sharing one slot,
# instead of being written as the base address.
#   /usr/lib/llvm-21/bin/llvm-mc -triple=x86_64-linux-gnu -filetype=obj \
#       -o x86_64-common-sym.o x86_64-common-sym.s
	.comm cbuf,8,8
	.data
	.globl here
here:	.quad cbuf
	.quad cbuf
