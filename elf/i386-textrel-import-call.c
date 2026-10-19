extern int ext_fn(int);
int foo(int x) { return ext_fn(x) + 1; }
