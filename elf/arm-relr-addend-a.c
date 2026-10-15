int x = 5;
int arr[4];
int *px = &x;
int *pbss = &arr[2];
static int f(void) { return 1; }
int (*pf)(void) = f;
