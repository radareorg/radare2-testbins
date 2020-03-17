
struct FcnTable {
	int (*some_func)(uint32_t a, uint64_t b);
};

typedef char *(*FcnPtr)(int a, const char *b);

