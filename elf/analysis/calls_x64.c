#include <stdio.h>

void func_X() {
	printf("%s\n", "Hello world");
}

void func_6() {
	func_X();
}

void func_5() {
	func_6();
}

void func_4() {
	func_5();
}

void func_3() {
	func_4();
}

void func_2() {
	func_3();
}

void func_1() {
	func_2();
}

void func_0() {
	func_1();
}

int main() {
	func_0();
	return 0;
}
