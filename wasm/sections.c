// emcc -g sections.c -o sections.wasm
#include <emscripten.h>
int int_glob_nonstatic;
float float_glob_nonstatic = 0.0f;
char char_array_global_nonstatic[32];

static int int_glob_static;
static float float_glob_static = 0.0f;
static char char_array_global_static[32];

static int static_int_sum(int int_arg0, int int_arg1) {
        return int_arg0 + int_arg1;
}

float nonstatic_float_subtract(float float_arg0, float float_arg1) {
        return float_arg0 - float_arg1;
}

static int atoi_via_import(const char *const_char_arg) {
        return EM_ASM_INT(parseInt($0), const_char_arg);
}

int main(int argc, char *argv[]) {
        int local_sum = 0;
        if (argc == 3) {
                int local_a = atoi_via_import(argv[1]);
                int local_b = atoi_via_import(argv[2]);
                local_sum = static_int_sum(local_a, local_b);
        }
        return local_sum;
}
