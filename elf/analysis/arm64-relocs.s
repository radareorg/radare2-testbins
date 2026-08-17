// compile with:
//   aarch64-linux-gnu-as -o arm64-relocs arm64-relocs.s
//
// local_target sits in its own section so every branch to it has to be
// relocated instead of being resolved by the assembler.

	.section .text.helper,"ax",%progbits
	.globl	local_target
	.type	local_target, %function
local_target:
	mov	w0, #7
	ret
	.size	local_target, .-local_target

	.text
	.globl	branch_relocs
	.type	branch_relocs, %function
branch_relocs:
	stp	x29, x30, [sp, #-16]!
	bl	local_target		// R_AARCH64_CALL26 to a defined symbol
	bl	extern_target		// R_AARCH64_CALL26 to an import
	tbz	w0, #3, local_target	// R_AARCH64_TSTBR14
	b.eq	local_target		// R_AARCH64_CONDBR19
	ldp	x29, x30, [sp], #16
	b	extern_tail		// R_AARCH64_JUMP26 tail call
	.size	branch_relocs, .-branch_relocs

	.section .rodata,"a",%progbits
	.align	3
	.globl	reloc_data
	.type	reloc_data, %object
reloc_data:
	.word	extern_target - .	// R_AARCH64_PREL32
	.word	local_target		// R_AARCH64_ABS32
	.xword	local_target		// R_AARCH64_ABS64
	.size	reloc_data, .-reloc_data
