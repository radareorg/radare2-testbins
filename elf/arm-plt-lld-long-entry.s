.text
.globl f
.type f,%function
f:
  bl foo
  bl bar
  bl baz
  bx lr
