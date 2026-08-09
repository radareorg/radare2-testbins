/* ppc32 PLT layout fixture with a TLS general-dynamic access. The GD sequence
   is what makes the linker emit the __tls_get_addr_opt glink entry, which
   carries an 8 word prefix ahead of the usual stub, so PLT entries here are not
   a uniform grid. Linked with --plt-align to also pad every stub to 32 bytes. */
static __thread int tvar;
__attribute__((noinline)) int add2(int a, int b) { return a + b; }
__attribute__((noinline)) int mul2(int a, int b) { return a * b; }
__attribute__((noinline)) int sub2(int a, int b) { return a - b; }
int get_tvar(int a, int b) { return tvar + add2 (a, b) + mul2 (a, b) + sub2 (a, b); }
int set_tvar(int v) { return tvar = v; }
