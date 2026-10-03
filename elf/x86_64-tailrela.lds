PHDRS {
	hdr PT_LOAD FILEHDR PHDRS FLAGS (4);
	text PT_LOAD FLAGS (5);
	data PT_LOAD FLAGS (6);
	dyn PT_DYNAMIC FLAGS (6);
	interp PT_INTERP FLAGS (4);
}
ENTRY (entry)
SECTIONS {
	. = 0x10000 + SIZEOF_HEADERS;
	.hash : { *(.hash) } :hdr
	.dynsym : { *(.dynsym) } :hdr
	.dynstr : { *(.dynstr) } :hdr
	. = ALIGN (0x100) + 0x400;
	.interp : { *(.interp) } :text :interp
	.text : { *(.text) } :text
	.plt : { *(.plt) } :text
	. = ALIGN (0x100) + 0x400;
	.dynamic : { *(.dynamic) } :data :dyn
	.got : { *(.got) } :data
	.got.plt : { *(.got.plt) } :data
	.data : { *(.data) } :data
	.rela.dyn : { *(.rela.dyn) } :data
	.rela.plt : { *(.rela.plt) } :data
	.bss : { *(.bss) . += 0x40; } :data
	/DISCARD/ : { *(.note*) *(.comment) *(.eh_frame*) }
}
