# clang -target aarch64-linux-gnu -c aarch64-common-tiny.s -o aarch64-common-tiny.o
	.comm tiny,1,1
	.comm tinygot,1,1
	.text
	.globl f
f:	adrp x0, tiny
	add x0, x0, :lo12:tiny
	adrp x1, :got:tinygot
	ldr x1, [x1, :got_lo12:tinygot]
	bl ext
	ret
