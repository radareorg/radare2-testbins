// R_AARCH64_PREL16 and R_AARCH64_PREL32 against undefined symbols, with zero and non-zero addends.
// Build: llvm-mc -triple=aarch64-linux-gnu -filetype=obj aarch64-prel16.s -o aarch64-prel16.o
	.text
	.globl	f
f:	ret
	.data
p16:	.hword	ext16 - .
p16a:	.hword	ext16 + 4 - .
p32:	.word	ext32 - .
p32a:	.word	ext32 + 8 - .
