extern "C" __global__ void ops(int *a, const int *b, float *f) {
	int i = threadIdx.x;
	int x = b[i];
	x = (x + 3) ^ (x << 2);
	if (x & 1) {
		a[i] = x * 7;
	} else {
		a[i] = x - 11;
	}
	f[i] = f[i] * 1.5f + 2.0f;
}
