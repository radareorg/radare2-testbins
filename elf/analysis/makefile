TARGETS = x86-simple x64-simple compiled.elf simple.elf simple64.elf \
	tiny.elf regdump.elf standard.elf simpleARM.elf simpleARM2.elf \
	no_sections.elf no_sechdr.elf dummy_secnames.elf dummy_shnum.elf \
	dummy_secvals.elf

all: $(TARGETS)

clean:
	rm -f $(TARGETS) *.o

simpleARM2.elf: simpleARM.asm consts.inc
	yasm -o simpleARM2.elf -D ABIR7 simpleARM.asm

%.elf: %.asm consts.inc
	yasm -o $@ $<
#	chmod +x ./$@

x86%.o: ../src/x86%.s
	nasm -f elf32 -o $@ $<

x64%.o: ../src/x64%.s
	nasm -f elf64 -o $@ $<

x86%: x86%.o
	ld -m elf_i386 -s -o $@ $<

x64%: x64%.o
	ld -m elf_x86_64 -s -o $@ $<

#osx:
	#@sh osx.sh

.PHONY: all clean
