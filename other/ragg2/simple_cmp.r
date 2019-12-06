write@syscall(4);
exit@syscall(1);

main@global(128) {
  .var0 = "hi!\n";
  .var1 = 1;
  .var2 = 2;
  if (.var1 < .var2) {
    write(1,.var0, 4);
  }
  exit(0);
}

