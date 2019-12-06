# GPL 3+ - Copyright (C) 2012  pancake, Edd Barrett, Simon Ruderich

bits 32

global _start
_start:
    ; Just a jump.
    call     test
test:
    pop     ebx

    mov     eax,  1  ; exit system call
    mov     ebx, 42  ; exit code
    int     0x80
