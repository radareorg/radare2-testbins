/* Stand-in for the libc that would define these, so tls.c can link -nostdlib.
   __tls_get_addr_opt is what turns on the linker's TLS optimization. */
	.text
	.globl __tls_get_addr
	.type __tls_get_addr,@function
__tls_get_addr:
	blr
	.size __tls_get_addr, .-__tls_get_addr
	.globl __tls_get_addr_opt
	.type __tls_get_addr_opt,@function
__tls_get_addr_opt:
	blr
	.size __tls_get_addr_opt, .-__tls_get_addr_opt
