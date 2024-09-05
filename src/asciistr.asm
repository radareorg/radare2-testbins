.arch x86
.bits 64

.text
.global _start
_start:
    lea rdi, [rip + lib]
    mov rax, 0x7ffff7c87bd0 ; puts
    call rax
    ret

.data
lib:
    .ascii "/home/nitanmarcel/shell/example/libhello.so"
lib2:
    .asciiz "/home/nitanmarcel/shell/example/libhello.so"
