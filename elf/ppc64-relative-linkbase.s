# ppc64 BE ET_DYN linked at a non-zero image base, so an applied
# R_PPC64_RELATIVE must add only the load bias (view base - link base), never the
# link base again. ELFv2, as lld cannot link ELFv1.
#   /usr/lib/llvm-21/bin/llvm-mc -triple=powerpc64-linux-gnu -filetype=obj \
#       -o ppc64-relative-linkbase.o ppc64-relative-linkbase.s
#   ld.lld-21 -shared -Bsymbolic --image-base=0x40000 \
#       -o ppc64-relative-linkbase.so ppc64-relative-linkbase.o
	.text
	.globl f
f:	blr
	.data
	.globl tab
tab:	.quad f
	.quad tab+8
	.quad 0x1234
