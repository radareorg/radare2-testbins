#include <stdint.h>

// R2R db/anal/globals
// llvm-objcopy --strip-all elf/anal-globals elf/anal-globals-stripped
// llvm-objcopy --strip-all mach0/anal-globals mach0/anal-globals-stripped
// The stripped Mach-O also clears LC_DYLD_EXPORTS_TRIE dataoff/datasize.
// Keep code/data addresses unchanged so both variants exercise the same accesses.

struct GlobalPair {
	int count;
	char tag;
};

int global_count = 7;
unsigned char global_byte = 3;
uint64_t global_wide = 0x12345678;
int global_zero;
const int global_limit = 11;
int global_array[3] = { 1, 2, 3 };
int *global_pointer = &global_count;
struct GlobalPair global_pair = { 5, 'x' };
static short global_static = 9;

int main(void) {
	static int local_static = 4;
	global_zero = global_count + global_byte + global_static + local_static;
	return global_zero + global_limit + global_array[1] + *global_pointer
		+ global_pair.count + (int)global_wide;
}
