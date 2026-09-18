# s390x ET_DYN linked at a non-zero image base, so an applied R_390_RELATIVE
# must add only the load bias (view base - link base), never the link base again.
#   /usr/lib/llvm-21/bin/llvm-mc -triple=s390x-linux-gnu -filetype=obj \
#       -o s390x-relative-linkbase.o s390x-relative-linkbase.s
#   ld.lld-21 -shared -Bsymbolic --image-base=0x40000 \
#       -o s390x-relative-linkbase.so s390x-relative-linkbase.o
	.text
	.globl f
f:	br %r14
	.data
	.globl tab
tab:	.quad f
	.quad tab+8
	.quad 0x1234
