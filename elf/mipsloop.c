main() {
	int a1 = 0x7a69;
	int v0 = 0;
	int v1 = 0xa;
	a1 ^= v0;
repeat:
	v0++;
	if (v0 != v1) {
		a1 ^= v0;
		goto repeat;
	}
	a1 ^= v0;
	printf ("0x%x\n", a1);
}
