public class World {
	int worldVar;
	int worldVar2;

	public World() {
		worldVar = 1;
		worldVar2 = 2;
	}

	public void foo(int num) {
		System.out.println ("world {}"+ new Integer(num).toString());
	}
}
