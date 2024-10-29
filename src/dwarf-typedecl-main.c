struct Foo {
	int bar;
	int baz;
};

struct Foo *new_foo() {
	void *malloc(unsigned long);

	struct Foo *f = malloc(sizeof(struct Foo));
	f->bar = 10;
	f->baz = 42;
	return f;
}

void foo();

int main()
{
	foo();
	return 0;
}
