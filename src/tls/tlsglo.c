#include <stdio.h>
_Thread_local int tls = 0;
int glo = 0;
int main() {
	printf ("%p\n", &tls);
	printf ("%p\n", &glo);
	return 0;
}
