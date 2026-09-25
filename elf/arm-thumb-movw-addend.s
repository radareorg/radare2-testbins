# thumbv7 ET_REL whose THM_MOVW_ABS_NC/THM_MOVT_ABS REL addend is negative and
# crosses a 64K boundary once the symbol is added, and a THM_JUMP19 whose
# addend puts the target outside the +-1MB a conditional b.w can reach, and
# one 640K away, inside that range but outside +-512K.
#   /usr/lib/llvm-21/bin/llvm-mc --triple=thumbv7-linux-gnu --filetype=obj \
#       -o arm-thumb-movw-addend.o arm-thumb-movw-addend.s
	.syntax unified
	.thumb
	.text
	.globl f
	.thumb_func
f:
	movw r0, :lower16:ext-0x100
	movt r0, :upper16:ext-0x100
	.reloc ., R_ARM_THM_JUMP19, ext2
	.inst.w 0xf03fafff
	.reloc ., R_ARM_THM_JUMP19, ext2
	.inst.w 0xf0208800
	b.w ext2
	bx lr
