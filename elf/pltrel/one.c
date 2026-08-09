__attribute__((noinline)) int add2(int a, int b) { return a + b; }
__attribute__((noinline)) int caller(int a, int b) { return add2 (a, b); }
