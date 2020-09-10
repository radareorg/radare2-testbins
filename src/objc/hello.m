#import "employee.h"

#import <Foundation/Foundation.h>

int main(int argc, const char* argv[]){
	@autoreleasepool {
		NSLog(@"Hello World Objective-C");
		Employee* ins = [[Employee alloc] init];
		[ins sayHello];
		[Employee sayHello];

		printf ("base %p\n", ins);
		void *base = [ins base];
		printf ("iii %p _username\n", (void*)([ins p0] - base));
		printf ("iii %p _firstName\n", (void*)([ins p1] - base));
		printf ("iii %p _shortWord\n", (void*)([ins p2] - base));
		printf ("iii %p _wideWord\n", (void*)([ins p3] - base));
		unsigned char *p = (__bridge void*)ins;
		int i;
		for (i = 0; i < 32; i++) {
			printf ("%02x ", p[i]);
		}
		printf ("\n");

		NSString *s = @"HELLO NSSTRING";
		printf ("%p\n", s);

#if defined (__i386__) || defined (__x86_64__)
		asm ("int3");
#else
		__builtin_trap ();
#endif
	}

	return 0;
}
