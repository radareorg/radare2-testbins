int counter;
long table[4];
char big[64] __attribute__((aligned(32)));

int bump(void) { counter++; table[1] = counter; return counter + big[3]; }
int get(void) { return counter; }
void set(int v) { counter = v; }
