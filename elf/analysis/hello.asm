.arch x86
.bits 32
mov edx, 0xe
mov ecx, msg
mov ebx, 1
mov eax, 4
int 0x80
mov eax, 1
int 0x80
msg:
.string "Hello, world!\n"
