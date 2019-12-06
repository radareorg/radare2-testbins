write@syscall(4);

main@globale(128, 128){
    .var0 = 9;
    .var8 = 5;
    .var16 = 6;
    if (.var0 < .var8){
        if (.var0 < .var16){
            write(1, "123456789", .var0);
        } else {
            write(1, "123456789", .var16);
        }
    } else {
        if (.var8 < .var16){
            write(1, "123456789", .var8);
        } else {
            write(1, "123456789", .var16);
        }
    }
    write(1, "\nhi,nice!\n", 10);
}
