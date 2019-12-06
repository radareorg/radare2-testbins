#include <stdio.h>

int main(int argc, char **argv){
    switch(argc) {
        case 1:
            puts("case 1");
            break;
        case 2:
        case 3:
        case 4:
            puts("case 2,3,4");
            break;
        case 5:
            puts("case 5");
            break;
        case 6:
            puts("case 6");
            break;
        case 7:
            puts("case 7");
            break;
        // case 8:
        //     puts("case 8");
        //     break;
        case 9:
            puts("case 9");
            break;
        // case 10:
        //     puts("case 10");
        //     break;
        case 11:
            puts("case 11");
            break;
        case 12:
            puts("case 12");
            break;
        case 13:
            puts("case 13");
            break;
        
        default:
            puts("default");
    }
    return 0;
}