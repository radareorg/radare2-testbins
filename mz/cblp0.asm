; Produces an MZ file whose size is a multiple of 512 bytes; i.e., with
; bytes_in_last_block = 0. Assumes the header added by the linker will also be
; a multiple of 512 bytes.
; https://github.com/radareorg/radare2/pull/19042

bits	16

segment	code
..start:
	xor	al, al
	mov	ah, 0x4c
	int	0x21

times	512-($-$$)	nop

segment	stack	stack
	resb	128
