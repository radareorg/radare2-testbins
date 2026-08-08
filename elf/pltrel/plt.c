/* PLT layout fixture: three locally defined functions reached through the PLT.
   Built once per arch/linker variant so the entry stride and header size can be
   checked: aarch64 -z pac-plt, x86-64 -z retpolineplt (lazy and -z now), ppc32.
   noinline keeps the calls from collapsing into caller, which would leave no
   relocations at all. */
__attribute__((noinline)) int add2(int a, int b) { return a + b; }
__attribute__((noinline)) int mul2(int a, int b) { return a * b; }
__attribute__((noinline)) int sub2(int a, int b) { return a - b; }
__attribute__((noinline)) int caller(int a, int b) { return add2 (a, b) + mul2 (a, b) + sub2 (a, b); }
