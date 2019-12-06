write@syscall(4);

main@global(128, 128) {
    .var0 = 2 - 1 & 3 - 2 - 1;
    .var0 = - 1 + 1 & 2 + 3 & 4 - 5 & 6 ^ 7 + 8;
    .var0 = 1 + 1 ^ 2 + 3 - 3 & 1 - 1;
    .var8 = *.var0 + 1 ^ &.var0 + 1 - 4;
    .var16 = .var8 + .var0;
    write(1, "123456789", .var16);
    .var16 = .var8 + .var0;
}
