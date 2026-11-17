# clang -target x86_64-linux-gnu -c x86_64-common-growth.s -o x86_64-common-growth.o
	.comm arr,0xff000,1
	.data
	.quad arr
	.quad ext+4095
	.quad ext2+4095
