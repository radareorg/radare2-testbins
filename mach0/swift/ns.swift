import Foundation
enum Foo {
	@objc
	class Bar:NSObject {
		private var a: Int = 0;
		func test() {
			print("Hello \(a)");
			a += 1;
		}
	}

	class Cow {
	}
}

let a = Foo.Bar();
a.test();
a.test();
