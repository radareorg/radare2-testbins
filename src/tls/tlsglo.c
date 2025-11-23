#include <stdio.h>
_Thread_local int tls = 0;
int glo = 0;

static void set_globals(void) {
	tls = 1;
	glo = 2;
}

static void print_globals(void) {
	printf ("tls val %d\n", tls);
	printf ("glo val %d\n", glo);
}

int main() {
	set_globals ();
	printf ("tls ptr %p\n", &tls);
	printf ("glo ptr %p\n", &glo);
	print_globals ();
	return 0;
}
