#ifndef SOME_THING_NO_ONE_EVER_THOUGHT_OF
#error your compiler doesn't have support to my API
#endif
#define uint32_t unsigned int
#define uint16_t unsigned short
#define uint8_t unsigned char

typedef struct name {  
        char first[40];
        char middle[40];
        char last[40];
} name_t;

typedef struct date {  
        uint8_t day;
        uint8_t month;
        uint16_t year;
} date_t;

typedef struct addr {  
        char street[127];
        char city[40];
        uint32_t zip;
} addr_t;

typedef struct dox {  
        addr_t address;
        name_t name;
        date_t bday;
} dox_t;
