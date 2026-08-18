/* ppc64 ELFv1 fixture: a 20-byte eager plt_call stub that is the whole .text.
 * --no-plt-thread-safe drops the lazy cmpldi/bnectr/b tail, so the stub is
 * std r2,40(r1); ld r12,d(r2); mtctr r12; ld r2,d+8(r2); bctr; the .text
 * section header size is then cut to 0x14 so the stub ends at the range end.
 *
 * powerpc64-e5500-linux-gnu-gcc -O2 -fPIC -shared -nostdlib -Wl,--build-id=none \
 *   -Wl,-z,max-page-size=0x1000 -Wl,-z,noseparate-code -Wl,--no-plt-thread-safe \
 *   -o ppc64v1-stub-eagerend.so ppc64v1-stub-eagerend.c
 * then: .text sh_size := 0x14 (shdr[7] + 0x20, big-endian)
 */
int leaf(int a, int b) { return a - b; }
int caller(int a, int b) { return leaf (a, b) + 1; }
