
// gcc game_of_thrones.c -no-pie -o game_of_thrones

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define DAENERYS  0
#define CERSEI    1
#define JON_SNOW  2
#define NED_STARK 3
#define TITLE_SIZE 60


struct character* characters[4] = {};

struct character {
    int64_t power;
    char* title;
};

int readint() {
    char buff[21];
    fgets(buff, 21, stdin);
    return atol(buff);
}

void characters_menu() {
    puts("1: DAENERYS");
    puts("2: CERSEI");
    puts("3: JON SNOW");
    puts("4: NED STARK");
    printf(">> ");
}

int get_character() {
    int character = 0;
    characters_menu();
    int option = readint();
    switch(option) {
        case 1:
            character = DAENERYS;
            break;
        case 2:
            character = CERSEI;
            break;
        case 3:
            character = JON_SNOW;
            break;
        case 4:
            character = NED_STARK;
            break;
        default:
            exit(-1);
    }
    return character;
}

void change_power() {
    int character = get_character();

    if(characters[character]){
        printf("Character power: ");
        scanf("%ld[^\n]", &(characters[character]->power));
        getchar();
    }
    else{
        puts("\nCreate a character!");
    }
}

void delete_character() {
    int character = get_character();

    if (characters[character]){
        if(characters[character]->title) {
            free(characters[character]->title);
            characters[character]->title = NULL;
        }
        free(characters[character]);
    }

    puts("Character deleted!");
}

void create() {
    char buff[TITLE_SIZE] = {0};
    int bytes_read = 0;
    int character = get_character();

    characters[character] = (struct character *) malloc(sizeof(struct character));

    if(!characters[character])
        exit(-1);

    printf("Character power: ");
    scanf("%ld", &(characters[character]->power));
    getchar();
}

void show_characters() {

    if (characters[DAENERYS] && characters[CERSEI] && characters[JON_SNOW] && characters[NED_STARK]) {
        printf("DAENERYS  %s. power: %ld\n", (characters[DAENERYS]->title  ? characters[DAENERYS]->title  : "Mother of Dragons"), characters[DAENERYS]->power);
        printf("CERSEI    %s. power: %ld\n", (characters[CERSEI]->title    ? characters[CERSEI]->title    : "Ruler of the Seven Kingdoms"), characters[CERSEI]->power);
        printf("JON SNOW  %s. power: %ld\n", (characters[JON_SNOW]->title  ? characters[JON_SNOW]->title  : "King of the Andals"), characters[JON_SNOW]->power);
        printf("NED STARK %s. power: %ld\n", (characters[NED_STARK]->title ? characters[NED_STARK]->title : "Lord of Winterfell"), characters[NED_STARK]->power);
    }
}

void change_titles() {
    char buff[TITLE_SIZE] = {0};
    int bytes_read = 0;
    int character = get_character();

    if (!characters[character])
        return;

    printf("Titles: ");

    // fgets(buff, TITLE_SIZE, stdin);
    bytes_read = read(0, buff, TITLE_SIZE - 1);

    if(buff[bytes_read - 1] == '\n')
        buff[bytes_read - 1] = '\x00';

    characters[character]->title = (char *) malloc(TITLE_SIZE);
    strncpy(characters[character]->title, buff, TITLE_SIZE);
}


void init() {
	setvbuf(stdin,  NULL, _IONBF, 0);
	setvbuf(stdout,  NULL, _IONBF, 0);
	setvbuf(stderr,  NULL, _IONBF, 0);
}

void print_menu() {
    puts("\n==========================");
    puts("1: Create character");
    puts("2: Change titles");
    puts("3: Change power");
    puts("4: Show characters");
    puts("5: Delete character");
    puts("6: Get flag");
    puts("==========================");
    printf(">> ");
}

void get_flag() {
    char flag[] = "\x38\x2e\x34\x35\x34\x23\x24\x6f\x22\x2e\x2c\x6e\x36\x20\x35\x22\x29\x7e\x37\x7c\x31\x1e\x74\x11\x36\x20\x34\x36\x20\x38\x2a";
    for (int i = 0; i < 31; i++)
        flag[i] ^= 0x41;
    puts(flag);
}

int main() {
    init();
    int option;

    while (1) {
        print_menu();
        option = readint();
        switch(option) {
            case 1:
                create();
                break;
            case 2:
                change_titles();
                break;
            case 3:
                change_power();
                break;
            case 4:
                show_characters();
                break;
            case 5:
                delete_character();
                break;
            case 6:
                get_flag();
                break;
        }
    }

    return 0;
}

