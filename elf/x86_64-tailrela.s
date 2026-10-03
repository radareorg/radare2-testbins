# x86_64-tailrela.so: a DSO whose reloc tables sit after .dynamic in the RW
# PT_LOAD, at a vaddr that differs from its file offset (see the .lds):
#   llvm-mc -triple=x86_64-linux-gnu -filetype=obj x86_64-tailrela.s -o t.o
#   ld.lld -shared --hash-style=sysv -z norelro -z max-page-size=0x100 \
#     -T x86_64-tailrela.lds t.o -o x86_64-tailrela.so
	.section .interp,"a"
	.asciz	"/lib/ld-musl-x86_64.so.1"

	.text
	.globl	entry
	.type	entry,@function
entry:
	movq	ext_obj@GOTPCREL(%rip), %rax
	leaq	local_ptr(%rip), %rdi
	call	ext_fn@PLT
	ret
	.size	entry, .-entry

	.data
	.globl	datum
	.type	datum,@object
datum:
	.quad	entry
	.quad	datum
	.quad	ext_obj
	.quad	ext_obj + 8
local_ptr:
	.quad	datum + 16
	.quad	local_ptr
	.size	datum, .-datum
