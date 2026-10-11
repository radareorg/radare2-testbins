# Thumb ET_REL with a blx to an SHN_ABS Thumb function, which ld turns into
# a bl to 0x08000100, next to a blx to the ARM function armfn that stays a
# blx; the R_ARM_ABS32 word keeps the Thumb bit, 0x08000101.
#   /usr/lib/llvm-21/bin/llvm-mc -triple=thumbv7-linux-gnueabi -filetype=obj \
#       -o arm-abs-thumb-blx.use.tmp arm-abs-thumb-blx.s
#   /usr/lib/llvm-21/bin/llvm-mc -triple=thumbv7-linux-gnueabi -filetype=obj \
#       --defsym DEF=1 -o arm-abs-thumb-blx.def.tmp arm-abs-thumb-blx.s
#   ld.lld-21 -r -o arm-abs-thumb-blx.o arm-abs-thumb-blx.use.tmp \
#       arm-abs-thumb-blx.def.tmp
	.syntax unified
	.thumb
.ifdef DEF
	.globl romfn
	.type romfn, %function
	.set romfn, 0x08000101
	.text
	.arm
	.globl armfn
	.type armfn, %function
armfn:	bx lr
.else
	.text
	.globl f
	.type f, %function
	.thumb_func
f:	blx romfn
	blx armfn
	bx lr
	.data
	.globl fnptr
fnptr:	.word romfn
.endif
