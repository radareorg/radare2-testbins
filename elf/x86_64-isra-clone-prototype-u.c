struct S { long x; long pad[8]; };
static __attribute__((noinline)) long f(struct S *p, double d, long a)
{
	return a * 3 + p->x + (long)d;
}
long g;
long use(long x, long y, double z)
{
	struct S s = { .x = y };
	struct S t = { .x = x };
	return f(&s, z, x) + f(&t, z, y);
}
void _start(void) { g = use(5, 2, 1.0); for(;;); }
