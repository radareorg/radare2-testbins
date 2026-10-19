# x86-64 object: 16 imports referenced at +0x40 and a 64-byte .bss, so
# the import slots need more room than the loader reserves before .bss.
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
	.bss
	.globl buf
buf:	.zero 64
