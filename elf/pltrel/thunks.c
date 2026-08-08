/* Thunk classification fixture, compiled -O2 so each wrapper becomes a tail
   call through the PLT. noinline on the leaves keeps the calls from folding.
   None of the top_* may be credited with a leaf's arguments. */
__attribute__((noinline)) int leaf2(int a, int b) { return a + b; }
__attribute__((noinline)) int leaf1(int a) { return a + 1; }
extern int flag;

/* supplies its own arguments, so it is not argument transparent */
__attribute__((noinline, visibility("hidden"))) int setwrap(void) { return leaf2 (1, 2); }
__attribute__((noinline)) int top_set(void) { return setwrap () + 1; }

/* two tail call exits, so no single callee can be attributed to the caller */
__attribute__((noinline, visibility("hidden"))) int forkwrap(int x, int y) {
	return flag? leaf1 (x): leaf2 (x, y);
}
__attribute__((noinline)) int top_fork(int a, int b) { return forkwrap (a, b) + 1; }
