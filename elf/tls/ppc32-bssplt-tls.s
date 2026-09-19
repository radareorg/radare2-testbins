# ppc32 BSS-PLT shared object whose executable .got holds a DTPMOD32 against
# the imported TLS symbol tv: the reloc belongs at its .got site, not a slot.
#   powerpc-linux-gnu-as -a32 -mbig -o ppc32-bssplt-tls.o ppc32-bssplt-tls.s
#   powerpc-linux-gnu-ld -shared --bss-plt -z max-page-size=0x1000 -z common-page-size=0x1000 -z norelro --hash-style=sysv -o ppc32-bssplt-tls.so ppc32-bssplt-tls.o
#   powerpc-linux-gnu-strip --strip-debug ppc32-bssplt-tls.so
	.text
	.globl f
f:
	addi 3, 31, tv@got@tlsgd
	bl __tls_get_addr(tv@tlsgd)
	bl puts
	blr
