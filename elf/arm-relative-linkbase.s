# arm32 ET_DYN linked at a non-zero image base, so an applied R_ARM_RELATIVE
# must add only the load bias (view base - link base), never the link base again.
# The table is DT_REL: each addend is the word already in the slot.
#   /usr/lib/llvm-21/bin/llvm-mc -triple=armv7-linux-gnueabi -filetype=obj \
#       -o arm-relative-linkbase.o arm-relative-linkbase.s
#   ld.lld-21 -shared -Bsymbolic --image-base=0x40000 \
#       -o arm-relative-linkbase.so arm-relative-linkbase.o
	.text
	.globl f
f:	bx lr
	.data
	.globl tab
tab:	.long f
	.long tab+4
	.long 0x1234
