int ext1(int a, int b);
int ext2(int a, int b);
int add2(int a, int b) { return a + b; }
int callext1(int a, int b) { return ext1(a, b); }
int callext2(int a, int b) { return ext2(a + 1, b); }
int add(int a, int b) { return add2(a, b); }
