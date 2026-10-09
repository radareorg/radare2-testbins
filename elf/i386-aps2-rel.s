# i386 ET_DYN whose REL relocs are Android-packed (DT_ANDROID_REL), so each
# RELATIVE slot's own word is its addend.
#   /usr/lib/llvm-21/bin/llvm-mc -triple=i386-linux-gnu -filetype=obj \
#       -o i386-aps2-rel.o i386-aps2-rel.s
#   ld.lld-21 -shared --pack-dyn-relocs=android -o i386-aps2-rel.so i386-aps2-rel.o
	.text
	.globl fn
fn:
	ret
	.section .rodata
str:
	.asciz "hello-aps2"
	.data
	.globl p1
p1:	.long str
