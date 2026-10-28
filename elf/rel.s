	.data
	.set B, 0x400000
ehdr:	.byte 0x7f,'E','L','F',2,1,1,0
	.quad 0
	.short 3, 183
	.long 1
	.quad B+0x300, 0x40, 0
	.long 0
	.short 64, 56, 2, 64, 0, 0
phdr:	.long 1, 7
	.quad 0, B, B, 0x320, 0x320, 0x1000
	.long 2, 6
	.quad 0x180, B+0x180, B+0x180, 0xa0, 0xa0, 8
	.balign 0x100, 0
dynstr:	.asciz ""
	.asciz "foo"
	.balign 0x10, 0
dynsym:	.quad 0, 0, 0
	.long 1
	.byte 0x12, 0
	.short 0
	.quad 0, 0
relaplt: .quad B+0x238, (1<<32)|1027, B+0x300
	.balign 0x20, 0
hash:	.long 1, 2, 1, 0, 0
	.balign 0x80, 0
dynamic: .quad 4, B+0x160, 5, B+0x100, 10, 5, 6, B+0x110, 11, 24, 23, B+0x140, 2, 24, 20, 7, 3, B+0x220, 0, 0
	.balign 0x20, 0
got:	.quad 0, 0, 0, B+0x300
	.balign 0x100, 0
code:	.long 0xd65f03c0, 0xd65f03c0, 0xd65f03c0, 0xd65f03c0, 0,0,0,0
