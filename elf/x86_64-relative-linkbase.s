# x86-64 ET_DYN linked at a non-zero image base, so an applied R_X86_64_RELATIVE
# must add only the load bias (view base - link base), never the link base again.
#   /usr/lib/llvm-21/bin/llvm-mc -triple=x86_64-linux-gnu -filetype=obj \
#       -o x86_64-relative-linkbase.o x86_64-relative-linkbase.s
#   ld.lld-21 -shared -Bsymbolic --image-base=0x40000 \
#       -o x86_64-relative-linkbase.so x86_64-relative-linkbase.o
	.text
	.globl f
f:	ret
	.data
	.globl tab
tab:	.quad f
	.quad tab+8
	.quad 0x1234
