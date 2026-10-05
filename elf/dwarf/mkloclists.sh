#!/bin/sh
# Regenerates loclists-x64-clang and loclists-aarch64-gcc: tiny static DWARF 5
# binaries whose optimised locals live in .debug_loclists (clang: DW_FORM_loclistx
# through DW_AT_loclists_base and DW_FORM_addrx; gcc: DW_FORM_sec_offset with
# DW_LLE_base_address/offset_pair/start_length). Needs clang-21, gcc (aarch64), ld.lld.
set -e
cat > loc.c <<'EOF'
int sink(int);
int work(int a, int b) {
	int x = a * 3;
	int y = sink(x);
	int z = y + b;
	return sink(z) + x;
}
int main(int argc, char **argv) { return work(argc, argc + 1); }
int sink(int v) { return v + 1; }
EOF
cat > start-x64.c <<'EOF'
int main(int, char **);
void _start(void) { int r = main(1, 0); __asm__ volatile ("mov %0, %%edi; mov $60, %%eax; syscall" :: "r"(r) : "rax", "rdi"); }
EOF
cat > start-a64.c <<'EOF'
int main(int, char **);
void _start(void) { long r = main(1, 0); __asm__ volatile ("mov x0, %0; mov x8, #93; svc #0" :: "r"(r) : "x0", "x8"); }
EOF
clang-21 -target x86_64-linux-gnu -gdwarf-5 -O2 -fno-inline -nostdlib -static -fuse-ld=lld -Wl,--build-id=none -o loclists-x64-clang loc.c start-x64.c
gcc -gdwarf-5 -O2 -fno-inline -nostdlib -static -Wl,--build-id=none -o loclists-aarch64-gcc loc.c start-a64.c
rm -f loc.c start-x64.c start-a64.c
