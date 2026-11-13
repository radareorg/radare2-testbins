	.intel_syntax noprefix
	.text
	.globl foo
	.type foo,@function
foo:
	ret
	.size foo, 1
	.section .plt,"ax",@progbits
stub:
	mov rax, qword ptr [rip + slot]
	mov qword ptr [rip + spill], rax
	call thunk
thunk:
	ret
	.data
slot:
	.quad foo
spill:
	.quad 0
