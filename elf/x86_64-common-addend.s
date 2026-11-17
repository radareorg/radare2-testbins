# clang -target x86_64-linux-gnu -c x86_64-common-addend.s -o x86_64-common-addend.o
	.comm arr,16384,16
	.data
	.quad arr
	.quad arr+0x2000
	.quad arr-8
	.quad arr+0x5000
