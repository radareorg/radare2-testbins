# clang -target x86_64-linux-gnu -c x86_64-common-bss-fit.s -o x86_64-common-bss-fit.o
	.comm arr,440,8
	.data
	.quad arr
	.quad arr+8
	.bss
	.zero 32
