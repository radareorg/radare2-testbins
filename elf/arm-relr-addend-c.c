static int t[8] = {1,2,3,4,5,6,7,8};
static int f(void) { return 1; }
int *tab[8] = { &t[0], &t[1], &t[2], &t[3], &t[4], &t[5], &t[6], &t[7] };
int (*pf)(void) = f;
int get(int i) { return *tab[i] + pf(); }
