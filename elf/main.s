	.abiversion 2
	.text
	.globl main
	.type main,@function
main:
0:	addis 2,12,.TOC.-0b@ha
	addi 2,2,.TOC.-0b@l
	.localentry main,.-main
	mflr 0
	std 0,16(1)
	stdu 1,-32(1)
	bl ext_fn
	nop
	addi 1,1,32
	ld 0,16(1)
	mtlr 0
	blr
	.size main,.-main
