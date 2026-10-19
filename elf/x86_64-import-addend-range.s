# x86-64 shared object, rela: data words against imports with addends.
# ext_a is referenced below and above its own address; ext_b with an
# addend past any slot r2 reserves, then with one that fits; ext_e and
# ext_f sit just inside and just past that limit; ext_c and ext_d plainly.
	.data
	.globl words
	.p2align 3
words:
	.quad	ext_a-8
	.quad	ext_a+8
	.quad	ext_b+0x2000
	.quad	ext_b+8
	.quad	ext_e+0xff8
	.quad	ext_f+0x1000
	.quad	ext_c
	.quad	ext_d
