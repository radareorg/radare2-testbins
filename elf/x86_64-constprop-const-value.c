static __attribute__((noinline)) long scale(long a, long k)
{
	return a * k + (a >> 3);
}
long g;
long use(long x, long y)
{
	return scale(x, 7) + scale(y, 7);
}
void _start(void) { g = use(5, 2); for(;;); }
