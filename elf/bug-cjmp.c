#include <stdio.h>
#define eprintf(x,y...) fprintf(stderr,x,##y)

main() {
	int var = 42;
	eprintf ("Hello %d\n", var;
}
