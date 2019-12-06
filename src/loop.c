#include <stdio.h>
#include <string.h>

int loop_cnt = 0;

void called_in_loop(void)
{
	loop_cnt++;
}

int main(int argc, char **argv)
{
	int i;

	for (i = 0; i < 3; i++) {
		called_in_loop();
	}
	return 0;
}
