#include <sys/syscall.h>
#include <time.h>
#include <unistd.h>

volatile int fasttime_phase = 0;

__attribute__((noinline))
void after_sleep(void) {
	fasttime_phase = 2;
}

int main(void) {
	struct timespec ts = {
		.tv_sec = 600,
		.tv_nsec = 0,
	};
	fasttime_phase = 1;
	syscall (SYS_nanosleep, &ts, 0);
#ifdef SYS_clock_nanosleep
	syscall (SYS_clock_nanosleep, CLOCK_MONOTONIC, 0, &ts, 0);
#endif
	after_sleep ();
	return fasttime_phase;
}
