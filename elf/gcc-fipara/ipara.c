#include <stdio.h>

static int counter;

// rdi/rsi confuses the decompiler because -fipa-ra
__attribute__((noinline)) static void func1(void)
{
    counter++;
}

__attribute__((noinline)) int use_after_call(int a, int b)
{
    func1();
    return a * 3 + b;   // a, b still in edi/esi after the call
}

int main(int argc, char **argv)
{
    printf("%d %d\n", use_after_call(argc, 7), counter);
    return 0;
}
