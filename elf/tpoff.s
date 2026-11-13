.section .tdata,"awT",@progbits
.p2align 12
.zero 0x2000
v: .long 1
.text
.globl f
f: movq v@GOTTPOFF(%rip),%rax
 ret
.section .rodata
.p2align 12
.zero 0x1000
.ascii "hello_tls_string\0"
