ENTRY(_start)
SECTIONS {
  . = 0x10000000;
  .text : { *(.text) }
  .sdata : { *(.sdata) }
  _SDA_BASE_ = ADDR(.sdata) + 0x100;
  /DISCARD/ : { *(.comment) *(.note*) *(.glink) }
}
