.arch x86
.bits 32
.include bins/other/rasm2/asm/inc_test.asm

mov ebx, 0
int 0x80
ret
