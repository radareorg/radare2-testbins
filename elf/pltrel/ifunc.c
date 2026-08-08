/* A default visibility GNU IFUNC gets a JUMP_SLOT relocation and a real PLT
   entry, which the local PLT naming has to pick up despite the LOOS type. */
static int real_foo(int x) { return x + 1; }
static void *resolve_foo(void) { return (void *)real_foo; }
int foo(int) __attribute__((ifunc ("resolve_foo")));
__attribute__((noinline)) int call_foo(int x) { return foo (x) + 1; }
