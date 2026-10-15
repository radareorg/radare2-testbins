struct S { long x; long pad[8]; };
static __attribute__((noinline)) long f(struct S *p, long a)
{
	return a * 3 + p->x;
}
long g;
long use(long x, long y)
{
	struct S s = { .x = y };
	struct S t = { .x = x };
	return f(&s, x) + f(&t, y);
}
void _start(void) { g = use(5, 2); for(;;); }
