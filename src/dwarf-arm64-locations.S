.text
.global _start
_start:
.type sp_slots,%function
sp_slots:
 .long 0xd10083ff, 0xf90007e0, 0xf9000be1
 .long 0xf94007e0, 0xf9400be1, 0x910083ff, 0xd65f03c0
sp_end:
.size sp_slots, .-sp_slots
.type bp_slot,%function
bp_slot:
 .long 0xd10083ff, 0xa9017bfd, 0x910043fd, 0xf81f83a0
 .long 0xf85f83a0, 0xa9417bfd, 0x910083ff, 0xd65f03c0
bp_end:
.size bp_slot, .-bp_slot
.type reg_values,%function
reg_values:
 .long 0xd65f03c0
reg_end:
.size reg_values, .-reg_values
.type fb_sp,%function
fb_sp:
 .long 0xd10083ff, 0xf90007e0, 0xf94007e0, 0x910083ff, 0xd65f03c0
fb_sp_end:
.size fb_sp, .-fb_sp
.type fb_bp,%function
fb_bp:
 .long 0xd10083ff, 0xa9017bfd, 0x910043fd, 0xf81f83a0
 .long 0xf85f83a0, 0xa9417bfd, 0x910083ff, 0xd65f03c0
fb_bp_end:
.size fb_bp, .-fb_bp
.type bregx_sp,%function
bregx_sp:
 .long 0xd10083ff, 0xf90007e0, 0xf94007e0, 0x910083ff, 0xd65f03c0
bregx_sp_end:
.size bregx_sp, .-bregx_sp

.section .debug_abbrev,"",%progbits
 .byte 1, 0x11, 1
 .byte 0x03, 0x08, 0x13, 0x05, 0, 0
 .byte 2, 0x24, 0
 .byte 0x03, 0x08, 0x3e, 0x0b, 0x0b, 0x0b, 0, 0
 .byte 3, 0x2e, 1
 .byte 0x03, 0x08, 0x11, 0x01, 0x12, 0x06
 .byte 0x40, 0x18, 0x49, 0x13, 0, 0
 .byte 4, 0x34, 0
 .byte 0x03, 0x08, 0x49, 0x13, 0x02, 0x18, 0, 0
 .byte 0

.macro function name, end, frame
 .byte 3
 .asciz "\name"
 .quad \name
 .long \end-\name
 .byte 1, \frame
 .long base_type-cu_start
.endm

.macro variable name, op, offset=-999
 .byte 4
 .asciz "\name"
 .long base_type-cu_start
 .if \offset == -999
  .byte 1, \op
 .else
  .byte 2, \op
  .sleb128 \offset
 .endif
.endm

.section .debug_info,"",%progbits
cu_start:
 .long cu_end-cu_version
cu_version:
 .short 4
 .long 0
 .byte 8
 .byte 1
 .asciz "dwarf-arm64-locations.S"
 .short 2
base_type:
 .byte 2
 .asciz "uint64_t"
 .byte 7, 8
 function sp_slots, sp_end, 0x6f
 variable first, 0x8f, 8
 variable second, 0x8f, 16
 .byte 0
 function bp_slot, bp_end, 0x6d
 variable local, 0x8d, -8
 .byte 0
 function reg_values, reg_end, 0x6f
 variable in_x29, 0x6d
 variable in_sp, 0x6f
 variable in_x0, 0x50
 .byte 0
 function fb_sp, fb_sp_end, 0x6f
 variable local, 0x91, 8
 .byte 0
 function fb_bp, fb_bp_end, 0x6d
 variable local, 0x91, -8
 .byte 0
 function bregx_sp, bregx_sp_end, 0x6f
 .byte 4
 .asciz "local"
 .long base_type-cu_start
 .byte 3, 0x92, 31, 8
 .byte 0
 .byte 0
cu_end:
