static __attribute__((noinline)) long f(long unused, double d, long a)
{
	return a * 3 + (long)(d * 2.0);
}
long g;
long use(long x, double y)
{
	return f(0, y, x) + f(1, y + 1.0, x + 7);
}
void _start(void) { g = use(5, 2.5); for(;;); }
