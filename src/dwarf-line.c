#include <stdio.h>

#include "/tmp/dwarf-line-foo.c"
#include "dwarf-line//bar.c"

struct Foo {};

struct Foo *new_foo() {
	return NULL;
}
void foo();

struct Bar {};

struct Bar *new_bar() {
	return NULL;
}
void bar();

int main(int a, const char **v) {
	while (a-- > 0) {
		printf ("Hello %d\n", a);
	}
	foo();
	bar();
	return 0;
}
