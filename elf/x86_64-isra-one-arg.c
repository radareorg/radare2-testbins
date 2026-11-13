struct S { long x; long pad[8]; };
static __attribute__((noinline)) long load(struct S *p)
{
	return p->x * 3;
}
long g;
long use(long x, long y)
{
	struct S s = { .x = y };
	struct S t = { .x = x };
	return load(&s) + load(&t);
}
void _start(void) { g = use(5, 2); for(;;); }
