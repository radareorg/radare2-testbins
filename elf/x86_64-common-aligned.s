# clang -target x86_64-linux-gnu -c x86_64-common-aligned.s -o x86_64-common-aligned.o
	.comm aligned,64,1048576
	.data
	.quad aligned
