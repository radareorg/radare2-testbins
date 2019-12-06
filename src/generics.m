// $ gcc generics.m -lobjc -framework Foundation
#import <Foundation/Foundation.h>

@interface MyCustomClass<T> : NSObject

- (void)doSomethingWithGeneric:(T)object;

@end

@implementation MyCustomClass

- (void)doSomethingWithGeneric:(id)object {
    //do something
}

@end

int main() {
	MyCustomClass<NSString *>* myCustomObject = [MyCustomClass new];
	[myCustomObject doSomethingWithGeneric:@"Some string"];
	// NOTE compiler warning, passing invalid generic type here
	[myCustomObject doSomethingWithGeneric:@12];
	return 0;
}

