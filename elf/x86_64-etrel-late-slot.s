# clang -target x86_64-linux-gnu -c x86_64-etrel-late-slot.s -o x86_64-etrel-late-slot.o
# 16 imports at +0x40 fill the room before .bss; a later plain import still needs its slot
	.text
	.globl f
f:	ret
	.data
	.quad ext_1+0x40
	.quad ext_2+0x40
	.quad ext_3+0x40
	.quad ext_4+0x40
	.quad ext_5+0x40
	.quad ext_6+0x40
	.quad ext_7+0x40
	.quad ext_8+0x40
	.quad ext_9+0x40
	.quad ext_10+0x40
	.quad ext_11+0x40
	.quad ext_12+0x40
	.quad ext_13+0x40
	.quad ext_14+0x40
	.quad ext_15+0x40
	.quad ext_16+0x40
	.quad late
	.bss
	.globl buf
buf:	.zero 64
