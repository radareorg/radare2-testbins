# s390x ET_DYN whose relative relocs are packed as DT_RELR, with the addends
# written in place, next to an R_390_64 that must be left alone.
#   /usr/lib/llvm-21/bin/llvm-mc -triple=s390x-linux-gnu -filetype=obj \
#       -o s390x-relr.o s390x-relr.s
#   ld.lld-21 -shared -z pack-relative-relocs --apply-dynamic-relocs \
#       -o s390x-relr.so s390x-relr.o
	.text
	.globl f
	.hidden f
f:	br %r14
	.globl g
g:	br %r14
	.data
	.p2align 3
tab:	.quad f
	.quad tab+8
	.quad f+16
	.quad g+4
	.quad 0x1234
