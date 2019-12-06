public class Hello {
	int localVar;
	static int localVar2;
	public Hello() {
		localVar = 1;
		localVar2 = 2;
	}
	public void foo(int num) {
		System.out.println ("foo {}"+ new Integer(num).toString());
		new World().foo(num);
	}
	public static void main(String[] args) {

		System.out.println("Findus");
		Hello hello = new Hello();
		hello.foo(3);
	}
}
