# GPL 3+ - Copyright (C) 2012  pancake, Edd Barrett, Simon Ruderich

bits 64

global _start
_start:
    ; Just a jump.
    call     test
test:
    pop     rbx

    mov     rax, 60  ; exit system call
    mov     rdi, 42  ; exit code
    syscall
