# Regenerate the local-PLT fixtures. Each is -nostdlib with no build-id and a
# 4k max page size so the files stay a few kB.
LDCOMMON=-shared -fPIC -nostdlib -Wl,--build-id=none,-z,max-page-size=0x1000,-z,noseparate-code
CLANG64=clang --target=x86_64-linux-gnu -fuse-ld=lld

all:
	$(CLANG64) -O1 $(LDCOMMON) -Wl,-z,retpolineplt -o x86_64-retpoline.so plt.c
	$(CLANG64) -O1 $(LDCOMMON) -Wl,-z,retpolineplt,-z,now -o x86_64-retpoline-now.so plt.c
	gcc -O1 $(LDCOMMON) -o aarch64-ifunc.so ifunc.c
	$(CLANG64) -O2 $(LDCOMMON) -o x86_64-thunks.so thunks.c bytewrap.S
	gcc -O1 $(LDCOMMON) -mbranch-protection=standard -Wl,-z,force-bti,-z,pac-plt -o aarch64-pac.so plt.c
	cp aarch64-pac.so aarch64-pac-noshdr.so
	python3 -c "import struct;p='aarch64-pac-noshdr.so';d=bytearray(open(p,'rb').read());struct.pack_into('<Q',d,0x28,0);struct.pack_into('<H',d,0x3c,0);struct.pack_into('<H',d,0x3e,0);open(p,'wb').write(d)"
	powerpc-linux-gnu-gcc -O1 $(LDCOMMON) -o ppc32be.so plt.c
	powerpc-linux-gnu-gcc -mlittle-endian -O1 $(LDCOMMON) -o ppc32le.so plt.c
	cp x86_64-retpoline.so x86_64-retpoline-noshdr.so
	python3 -c "import struct;p='x86_64-retpoline-noshdr.so';d=bytearray(open(p,'rb').read());struct.pack_into('<Q',d,0x28,0);struct.pack_into('<H',d,0x3c,0);struct.pack_into('<H',d,0x3e,0);open(p,'wb').write(d)"
	# the first and last call thunks exchanged, which a linker reaches by emitting
	# one thunk per input file rather than one per relocation
	cp ppc32be.so ppc32be-swapped.so
	python3 -c "p='ppc32be-swapped.so';d=bytearray(open(p,'rb').read());a,b=0x260,0x280;d[a:a+16],d[b:b+16]=d[b:b+16],d[a:a+16];open(p,'wb').write(d)"
