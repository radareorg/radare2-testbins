int add2(int a, int b);

int add(int a, int b) {
    return add2(a,b);
}

int add2(int a, int b) {
    return a + b;
}
