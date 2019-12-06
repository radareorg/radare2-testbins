#import <Foundation/Foundation.h>
//@import Foundation;

@interface Test : NSObject {
	/* instance variables */
	int num;
}
- (void)sayHello:(int)i;
@end

int main() {
	Test *o = [[Test alloc] init];
	[o sayHello:3];
	return 0;
}

@implementation Test
// _c_Test__callMeNot
// static method
+ (void)callMeNot {
	NSLog (@"Hahha");
}

-(id) init {
	self = [super init];
	return self;
}
- (void)sayLong:(unsigned long long)lllll {
	NSLog (@"Hello World ");
}
// _i_Test__sayHello__
- (void)sayHello3:(int)n :(int)q {
	NSLog (@"Hello World ");
}
- (void)sayHello:(int)n {
	NSLog (@"Hello World ");
}
- (void)sayHello2 {
	NSLog (@"Hello World ");
}
@end
