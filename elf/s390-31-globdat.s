# Source of s390-31-globdat.so, a 31-bit (ELFCLASS32) s390 DSO. No toolchain
# here targets 31-bit s390, so this is linked for ppc32 and retargeted:
#   /usr/lib/llvm-21/bin/llvm-mc -triple=powerpc-linux-gnu -filetype=obj \
#       -o s390-31-globdat.o s390-31-globdat.s
#   ld.lld-21 -shared -Bsymbolic -o s390-31-ppc32.so s390-31-globdat.o
#   python3 mks390-31.py s390-31-ppc32.so s390-31-globdat.so
	.text
	.globl f
f:	blr
	.data
	.globl tab
tab:	.long f
	.long tab+4
	.long 0x11223344
	.long 0x55667788
