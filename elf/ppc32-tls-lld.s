	.text
	.globl f
f:
	addi 3, 31, tv@got@tlsgd
	bl __tls_get_addr(tv@tlsgd)
	addi 3, 31, ld@got@tlsld
	bl __tls_get_addr(ld@tlsld)
	lwz 3, iv@got@tprel(31)
	blr
	.section .tbss,"awT",@nobits
	.globl tv
tv: .zero 4
	.globl iv
iv: .zero 4
ld: .zero 4
