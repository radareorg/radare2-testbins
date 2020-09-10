#include "employee.h"

@implementation Employee

+ (void)sayHello {
	NSLog(@"Hello Class");
}
- (void)sayHello {
	NSLog(@"Hello Instance");
}
- (void)helloWorld{
	NSLog(@"Hello World");
}
- (void*)p0 { return &_username; }
- (void*)p1 { return &_firstName; }
- (void*)p2 { return &_shortWord; }
- (void*)p3 { return &_wideWord; }
- (void*)base { return (__bridge void*)self; }

@end
