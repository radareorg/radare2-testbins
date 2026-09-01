# thumbv7 ET_REL carrying R_ARM_THM_MOVW_ABS_NC, THM_MOVT_ABS, THM_JUMP19 (beq.w,
# the T3 conditional encoding) and THM_JUMP24 (plain b.w).
#   llvm-mc --triple=thumbv7-linux-gnu --filetype=obj -o arm-thumb-movw.o arm-thumb-movw.s
	.syntax unified
	.thumb
	.text
	.globl f
	.thumb_func
f:
	movw r0, :lower16:ext
	movt r0, :upper16:ext
	beq.w ext2
	b.w ext2
	bx lr
