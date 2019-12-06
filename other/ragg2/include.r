write@syscall(4);

TMPDIR1@alias("/tmp");
TMPDIR2@alias("/tmp");

ifelse.r@include(TMPDIR1);
mathop.r@include(TMPDIR2)
