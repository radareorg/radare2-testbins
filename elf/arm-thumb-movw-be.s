# big-endian thumbv7 ET_REL: THM_MOVW_ABS_NC/THM_MOVT_ABS with a negative REL
# addend, THM_JUMP19 to a local thumb function and one whose addend has bit 18
# different from bit 19, and a movw/movt r3 against a defined .data label.
# llvm-mc rejects the out-of-range addend, so use gas:
#   arm-linux-gnueabi-as -EB -march=armv7-a -o arm-thumb-movw-be.o arm-thumb-movw-be.s
	.syntax unified
	.thumb
	.text
	.globl back
	.thumb_func
back:
	bx lr
	.globl f
	.thumb_func
f:
	movw r0, :lower16:ext-4
	movt r0, :upper16:ext-4
	bne.w back
	beq.w ext2+0x44000
	bx lr
	.globl g
	.thumb_func
g:
	movw r3, :lower16:.Lv+8
	movt r3, :upper16:.Lv+8
	bx lr
	.data
.Lv:
	.word 0, 0, 0, 0
