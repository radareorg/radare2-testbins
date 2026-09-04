import struct, sys
SZ=0xa00
buf=bytearray(SZ)
def w(off,data): buf[off:off+len(data)]=data
# ---- program headers
PT_LOAD=1; PT_DYNAMIC=2
def phdr(t,fl,off,va,fsz,msz,al): return struct.pack("<IIQQQQQQ",t,fl,off,va,va,fsz,msz,al)
ph =phdr(PT_LOAD,   6,0,0x0000,SZ,SZ,0x1000)              # RW  , file[0,SZ)
ph+=phdr(PT_LOAD,   5,0,0x5000,SZ,SZ,0x1000)              # R-X , SAME file[0,SZ)
ph+=phdr(PT_DYNAMIC,6,0x200,0x200,0x90,0x90,8)
# ---- ehdr
e=struct.pack("<4sBBBBB7xHHIQQQIHHHHHH", b"\x7fELF",2,1,1,0,0,
              3,          # ET_DYN
              62,         # EM_X86_64
              1, 0x5100,  # entry inside LOAD1
              0x40,       # phoff
              0,          # shoff  (no sections)
              0, 64, 56, 3, 0, 0, 0)
w(0,e); w(0x40,ph)
# ---- dynamic @0x200 (vaddr 0x200, inside LOAD0)
D=[(7,0x300),(8,24*2),(9,24),(6,0x400),(11,24),(5,0x500),(10,16),(0,0)]
w(0x200, b"".join(struct.pack("<qQ",a,b) for a,b in D))
# ---- .rela.dyn @0x300 : two R_X86_64_RELATIVE, one in each segment
R_X86_64_RELATIVE=8
w(0x300, struct.pack("<QQq",0x5800,R_X86_64_RELATIVE,0x5100)   # site inside LOAD1
       + struct.pack("<QQq",0x0900,R_X86_64_RELATIVE,0x0100))  # site inside LOAD0
# ---- symtab/strtab stubs
w(0x400, b"\0"*24)
w(0x500, b"\0"+b"ovl\0"+b"\0"*11)
# marker bytes so a wrong write is visible
w(0x800, b"\xAA"*8)   # == LOAD0 vaddr 0x800 AND LOAD1 vaddr 0x5800
w(0x900, b"\xBB"*8)   # == LOAD0 vaddr 0x900 AND LOAD1 vaddr 0x5900
with open(sys.argv[1], "wb") as f:
    f.write(bytes(buf))
