#import <Foundation/Foundation.h>

@interface Employee : NSObject

@property (retain) NSString* username;
@property (retain) NSString* firstName;
@property (readonly) short shortWord;
@property (readonly) uint64_t wideWord;

+ (void)sayHello;
- (void)sayHello;
- (void)helloWorld;
- (void*)p0;
- (void*)p1;
- (void*)p2;
- (void*)p3;
- (void*)base;

@end
