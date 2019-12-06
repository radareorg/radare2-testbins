write@syscall(4);

main();

main@global(128, 128){
    .var0 = 0x400a50;
    .var1 = "zz,dawang";
    test(.var0, "Hello", .var1);
}

test@global(128, 128){
    write(.arg0, .arg1, .arg2);
}
