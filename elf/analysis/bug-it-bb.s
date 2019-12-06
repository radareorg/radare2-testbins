; compile with:
;   arm-linux-gnu-as -o bug-it-bb.o bug-it-bb.s
;   arm-linux-gnu-ld -s -o bug-it-bb.bin bug-it-bb.o
.data

msg_a:
    .ascii      "R0 = 8\n"
len_a = . - msg_a

msg_b:
    .ascii      "R0 != 8\n"
len_b = . - msg_b

.text

.globl _start
.syntax unified

.code 16
some_IT_func:
    push {LR}
    cmp r0, r1
    itte eq
    addeq r0, r0, #1
    addeq r0, r0, #1
    movne r0, #4
    pop {pc}


.code 32
_start:
    mov r0, #6
    mov r1, r0

    blx some_IT_func

    ldreq r1, =msg_b
    ldreq r2, =len_b
 
    cmp r0, #8
    ldreq r1, =msg_a
    ldreq r2, =len_a
    mov r0, #1
    mov r7, #4
    swi #0

    mov r0, #0
    mov r7, #1
    swi #0
