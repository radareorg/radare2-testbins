# x86-64 relocs against SHN_ABS symbols, whose values are constants and must
# be written unchanged at any base. abshit lies inside the first PT_LOAD and
# abszero is a defined value of 0, not an unresolved reference.
#   /usr/lib/llvm-21/bin/llvm-mc -triple=x86_64-linux-gnu -filetype=obj \
#       -o x86_64-abs-sym.o.tmp x86_64-abs-sym.s
#   ld.lld-21 -r --defsym=absval=0x1234 --defsym=abshit=0x400100 \
#       --defsym=abszero=0 -o x86_64-abs-sym.o x86_64-abs-sym.o.tmp
#   ld.lld-21 -shared --image-base=0x400000 --defsym=absval=0x1234 \
#       --defsym=abshit=0x400100 --defsym=abszero=0 -o x86_64-abs-sym.so x86_64-abs-sym.o.tmp
#   llvm-objcopy-21 --strip-sections x86_64-abs-sym.so x86_64-abs-sym-noshdr.so
	.data
	.globl here
here:	.quad absval
	.quad abshit
	.quad abszero
	.quad here
