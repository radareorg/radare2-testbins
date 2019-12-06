// https://software.intel.com/sites/landingpage/IntrinsicsGuide/#expand=0,85&techs=SSE2
#include <emmintrin.h>

__m128i a = {0x0807060504030201,0x100f0e0d0c0b0a09};
__m128i b = {0x2222222211111111,0x4444444433333333};
int main(void)  {
	__m128i res = _mm_add_epi16(a,b);
	return 0;
}
