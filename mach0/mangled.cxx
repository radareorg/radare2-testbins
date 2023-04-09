#include <stdlib.h>

int foo() {
	return 1;
}
int foo(int a) {
	return a + 1;
}
int foo(int a, int b) {
	return a + foo(b);
}

int main(int argc, char **argv) {
	int a = argc;
	int b = atoi (argv[0]);
	return foo() + foo(a) + foo(a, b);
}
