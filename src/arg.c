int call(const char *a, const char *b) {
	int localvar = (int)(b - a);
	return printf ("%s %s %d\n", a, b, localvar);
}

main() {
	return call("hello", "world");
}
