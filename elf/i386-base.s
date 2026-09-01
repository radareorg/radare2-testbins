# i386 ET_DYN pair with a NONZERO link-time image base (0x10000): every other i386
# ET_DYN in the tree has base 0, which makes R_386_RELATIVE (B + A) the identity
# and untestable. The RELA twin leaves the slot word unmaterialized, so a correct
# apply must write it; the REL twin's in-place word must stay unchanged.
#   llvm-mc --triple=i386-linux-gnu --filetype=obj -o i386-base.o i386-base.s
#   ld.lld -m elf_i386 -shared --image-base=0x10000 -z rel -z max-page-size=0x1000 --build-id=none -o i386-base10000-rel.so i386-base.o
#   ld.lld -m elf_i386 -shared --image-base=0x10000 -z rela --no-apply-dynamic-relocs -z max-page-size=0x1000 --build-id=none -o i386-base10000-rela.so i386-base.o
# lp must point at a non-exported label: an exported one gets R_386_32, not RELATIVE.
	.text
	.globl	entry
entry:
	call	ext@PLT
	movl	gvar@GOT(%ebx), %eax
	movl	(%eax), %eax
	ret
local:
	ret
	.data
	.globl	gvar
gvar:
	.long	7
	.globl	lp
lp:
	.long	local
