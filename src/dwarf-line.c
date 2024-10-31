#include <stdio.h>

int main(int a, const char **v) {
	while (a-- > 0) {
		printf ("Hello %d\n", a);
	}
	return 0;
}
