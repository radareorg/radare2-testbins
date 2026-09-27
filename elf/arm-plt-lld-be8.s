# a BE8 ARM shared object with an lld plt: big-endian data, little-endian code,
# 32-byte plt header and 16-byte entries. Two jump slots, foo and bar.
#   llvm-mc -triple=armebv7-linux-gnueabi -filetype=obj -o t.o arm-plt-lld-be8.s
#   ld.lld -shared --be8 -o arm-plt-lld-be8.so t.o
	.syntax unified
	.arm
	.text
	.globl f
	.type f, %function
f:
	push {r4, lr}
	bl foo
	bl bar
	pop {r4, pc}
