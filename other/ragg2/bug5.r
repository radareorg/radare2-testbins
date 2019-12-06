write@syscall(4);

main@global(128,128){
    .var0 = 0;
    .var4 = 16;
    while (.var0 < .var4) {
        write(1, "zz, dawang\n", 10);
        .var0 = 4 + .var0;
    }
    if (.var0 == .var4) {
        main();
    }
}
