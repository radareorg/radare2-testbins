/* test for following a forking child -jduck */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <sys/wait.h>

int done = 0;

void break_on_me(void) {
	printf ("child in leaf!\n");
}

void child_proc(void) {
	fprintf (stderr, "child process %d lives!\n", getpid());
	//printf("break_on_me is at 0x%zx\n", (size_t)&break_on_me);
	break_on_me ();
	printf ("child process terminating!\n");
	exit (37);
}

int main(int argc, char **argv) {
	pid_t cpid;

	fprintf (stderr, "main process %d started!\n", getpid ());

	cpid = fork ();
	if (cpid == -1) {
		perror ("fork");
	} else if (cpid == 0) {
		child_proc ();
		/* not reached */
	}

	wait (NULL); // wait for child

	printf ("main exiting!\n");

	return 0;
}
