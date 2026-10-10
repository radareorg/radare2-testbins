# Thumb ET_REL with a branch to an SHN_ABS Thumb function: the bl lands on
# 0x08000100, while the R_ARM_ABS32 word keeps the Thumb bit, 0x08000101.
# A blx to it becomes a bl, as ld does; a blx to the ARM function armfn
# stays a blx.
#   /usr/lib/llvm-21/bin/llvm-mc -triple=thumbv7-linux-gnueabi -filetype=obj \
#       -o arm-abs-thumb.use.tmp arm-abs-thumb.s
#   /usr/lib/llvm-21/bin/llvm-mc -triple=thumbv7-linux-gnueabi -filetype=obj \
#       --defsym DEF=1 -o arm-abs-thumb.def.tmp arm-abs-thumb.s
#   ld.lld-21 -r -o arm-abs-thumb.o arm-abs-thumb.use.tmp arm-abs-thumb.def.tmp
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
f:	bl romfn
	blx romfn
	blx armfn
	bx lr
	.data
	.globl fnptr
fnptr:	.word romfn
.endif
