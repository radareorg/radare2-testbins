public class test {
	public static int result (int arg0, int arg1) {
		return arg0 + arg1;
	}
	public static void main(String[] args) {
		int fuck = 33;
		int bar = 44;
		System.out.println(new Integer(result(3,5)).toString());
		System.out.println(new Integer(result(fuck,bar)).toString());
	}
}
