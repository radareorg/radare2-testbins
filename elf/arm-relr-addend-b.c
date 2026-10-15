int x = 5;
static int f(void) { return 1; }
int *p1 = &x; int *p2 = &x; int *p3 = &x; int (*pf)(void) = f;
