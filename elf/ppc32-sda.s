# ppc32 BE ET_EXEC pair for the _SDA_BASE_ agree/disagree guard: the -agree link
# script sets _SDA_BASE_ = .sdata+0x8000 (anal.gp seeds), -disagree +0x100 (stays 0).
# The loads are r2-relative by hand (Wind River/Diab convention, not EABI r13).
#   powerpc-linux-gnu-as -mbig -mregnames -o ppc32-sda.o ppc32-sda.s
#   powerpc-linux-gnu-ld -N -z max-page-size=0x100 -T ppc32-sda-agree.ld -o ppc32-sda-agree ppc32-sda.o
#   powerpc-linux-gnu-ld -N -z max-page-size=0x100 -T ppc32-sda-disagree.ld -o ppc32-sda-disagree ppc32-sda.o
	.text
	.globl _start
_start:
	bl get_sda
	li 0,1
	sc
	.globl get_sda
	.type get_sda,@function
get_sda:
	lwz 3,-0x8000(2)
	lwz 4,-0x7ffc(2)
	add 3,3,4
	blr
	.size get_sda,.-get_sda
	.section .sdata,"aw",@progbits
	.globl gv1
gv1:
	.long 0x2a
	.globl gv2
gv2:
	.long 0x539
