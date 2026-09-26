# arm ET_REL whose relocs target a defined thumb function tf (st_value 9):
# ABS32, REL32, TARGET1 and arm-mode MOVW_ABS_NC/MOVW_PREL_NC carry the thumb
# bit ((S + A) | T); THM_CALL, MOVT_ABS, ABS16 and a symbol-less TARGET1 do not.
#   arm-linux-gnueabi-as -o arm-thumb-bit.o arm-thumb-bit.s
	.syntax unified
	.text
	.thumb
	.align 2
	.globl caller
	.type caller, %function
	.thumb_func
caller:	bl tf
	bx lr
	.globl tf
	.type tf, %function
	.p2align 2
	.thumb_func
tf:	bx lr
	.arm
	.align 2
	.globl armf
	.type armf, %function
armf:
	movw r0, #:lower16:tf
	movt r0, #:upper16:tf
	movw r1, #:lower16:(tf - (. + 8))
	bx lr
	.data
	.align 2
	.word tf
	.short tf
	.short 0
	.word tf - .
	.word tf(target1)
	.reloc ., R_ARM_TARGET1
	.word 0x10
