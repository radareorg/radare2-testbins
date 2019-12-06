write@syscall(1);

main@global(128, 128){
    .var0 = 1;
    .var1 = 2;
    test("Hello\ntest");
}

test@global(128, 128){
    .var0 = "World";
    write(1, .arg0, 6);
}
