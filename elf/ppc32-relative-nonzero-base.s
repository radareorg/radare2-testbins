# ppc32 BE ET_DYN linked at a non-zero image base with DT_REL relocs, so the
# R_PPC_RELATIVE value rule is observable. The site holds the link-time vaddr of
# `target` as its implicit addend; only a rebased view (r2 -B) separates
# "map the addend into the view" from "load base + addend" from "no addend read".
#   /usr/lib/llvm-21/bin/llvm-mc -triple=powerpc-linux-gnu -filetype=obj \
#       -o ppc32-relative-nonzero-base.o ppc32-relative-nonzero-base.s
#   ld.lld-21 -shared -EB -z rel --image-base=0x40000000 -s -z norelro \
#       --build-id=none -z noseparate-code --no-eh-frame-hdr \
#       -o ppc32-relative-nonzero-base.so ppc32-relative-nonzero-base.o
	.text
	.globl f
f:
	blr
	.data
	.hidden target
	.globl target
target:
	.long 0x11223344
	.globl ptr_target
ptr_target:
	.long target
