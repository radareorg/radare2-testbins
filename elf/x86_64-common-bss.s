# clang -target x86_64-linux-gnu -c x86_64-common-bss.s -o x86_64-common-bss.o
	.comm arr,4096,16
	.comm small,8,8
	.data
	.quad arr
	.quad arr+8
	.quad small
	.bss
	.zero 32
