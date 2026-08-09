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
	# lld grows bti-only entries to 24 bytes where bfd keeps them at 16
	clang --target=aarch64-linux-gnu -fPIC -O1 -mbranch-protection=bti -c plt.c -o bti.o
	ld.lld -shared -z force-bti --build-id=none -z max-page-size=0x1000 -z noseparate-code -o aarch64-bti-lld.so bti.o
	# default page size keeps .plt far enough from r30 to force the addis thunk form
	clang --target=powerpc-linux-gnu -fPIC -O1 -c plt.c -o ppc32.o
	ld.lld -m elf32ppc -shared --build-id=none -o ppc32be-lld.so ppc32.o
	rm -f bti.o ppc32.o
	# bfd keeps bti entries at 16 bytes, and with no sections only the entry bytes say so
	gcc -O1 $(LDCOMMON) -mbranch-protection=bti -Wl,-z,force-bti -o aarch64-bti-bfd-noshdr.so plt.c
	python3 -c "import struct;p='aarch64-bti-bfd-noshdr.so';d=bytearray(open(p,'rb').read());struct.pack_into('<Q',d,0x28,0);struct.pack_into('<H',d,0x3c,0);struct.pack_into('<H',d,0x3e,0);open(p,'wb').write(d)"
	# one relocation leaves no stride to measure between two got slots
	$(CLANG64) -O1 $(LDCOMMON) -Wl,-z,retpolineplt -o x86_64-retpoline-one-noshdr.so one.c
	python3 -c "import struct;p='x86_64-retpoline-one-noshdr.so';d=bytearray(open(p,'rb').read());struct.pack_into('<Q',d,0x28,0);struct.pack_into('<H',d,0x3c,0);struct.pack_into('<H',d,0x3e,0);open(p,'wb').write(d)"
	# --plt-align pads every stub to 32, and the tls glink entry keeps its 8 word
	# prefix on top of that, so the entries are not a uniform grid
	powerpc-linux-gnu-gcc -O1 $(LDCOMMON) -o tlsdef.so tlsdef.S
	powerpc-linux-gnu-gcc -O1 $(LDCOMMON) -Wl,--plt-align=5 -o ppc32be-align-tls.so tls.c ./tlsdef.so
	rm -f tlsdef.so
	# a lone bti entry has no next entry to measure the stride against; gcc because
	# clang resolves the local ifunc call before it can reach the plt
	gcc -fPIC -O1 -mbranch-protection=bti -c ifunc.c -o btiifunc.o
	ld.lld -shared -z force-bti --build-id=none -z max-page-size=0x1000 -z noseparate-code -o aarch64-bti-lld-one.so btiifunc.o
	rm -f btiifunc.o
	# without the sections that entry has neither a neighbour nor a size to divide,
	# so only the nops padding it out say how long it is
	cp aarch64-bti-lld-one.so aarch64-bti-lld-one-noshdr.so
	python3 -c "import struct;p='aarch64-bti-lld-one-noshdr.so';d=bytearray(open(p,'rb').read());struct.pack_into('<Q',d,0x28,0);struct.pack_into('<H',d,0x3c,0);struct.pack_into('<H',d,0x3e,0);open(p,'wb').write(d)"
