public class Hello {
	private String who;

	public Hello (String who) {
		this.who = who;
	}

	public void say () {
		System.out.println ("Hello "+who);
	}

	public static void main(String[] args) {
		new Hello ("World").say ();
	}
}
