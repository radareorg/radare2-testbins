	.file	"prueba.c"
	.machinemode zarch
	.machine "zEC12"
.text
	.section	.rodata
	.align	2
.LC0:
	.string	"Hola mundo"
.text
	.align	8
.globl main
	.type	main, @function
main:
.LFB0:
	.cfi_startproc
	stmg	%r11,%r15,88(%r15)
	.cfi_offset 11, -72
	.cfi_offset 12, -64
	.cfi_offset 13, -56
	.cfi_offset 14, -48
	.cfi_offset 15, -40
	lay	%r15,-160(%r15)
	.cfi_def_cfa_offset 320
	lgr	%r11,%r15
	.cfi_def_cfa_register 11
	larl	%r2,.LC0
	brasl	%r14,puts@PLT
	lhi	%r1,0
	lgfr	%r1,%r1
	lgr	%r2,%r1
	lmg	%r11,%r15,248(%r11)
	.cfi_restore 15
	.cfi_restore 14
	.cfi_restore 13
	.cfi_restore 12
	.cfi_restore 11
	.cfi_def_cfa 15, 160
	br	%r14
	.cfi_endproc
.LFE0:
	.size	main, .-main
	.ident	"GCC: (Ubuntu 9.3.0-17ubuntu1~20.04) 9.3.0"
	.section	.note.GNU-stack,"",@progbits
