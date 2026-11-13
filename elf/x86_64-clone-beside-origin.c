struct S { long x; long pad[8]; };
__attribute__((noinline)) long mix(struct S *p, long a, long k)
{
	long r = 0;
	for (long i = 0; i < k; i++)
		r += (a ^ i) / k + p->x;
	return r;
}
long g;
long use(long x, long y)
{
	struct S s = { .x = y };
	struct S t = { .x = x };
	return mix(&s, x, 9) + mix(&t, y, 9);
}
void _start(void) { struct S u = { .x = g }; g = use(5, 2) + mix(&u, g, (long)&g); for(;;); }
