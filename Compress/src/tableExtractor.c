#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include "bSwap.h"
#include "yaz0.c"

#define UINTSIZE 0x1000000
#define COMPSIZE 0x2000000

/* Structs */
typedef struct
{
    uint32_t startV;
    uint32_t endV;
    uint32_t startP;
    uint32_t endP;  
}
table_t;

/* Functions */
uint32_t findTable();
table_t getTableEnt();
void errorCheck(int, char**);

/* Globals */
uint8_t* inROM;
uint32_t* fileTab;

int main(int argc, char** argv)
{
    FILE* file;
    int32_t tabStart, tabSize, tabCount, i;
    uint8_t* refTab;
    table_t tab;

    errorCheck(argc, argv);

    /* Open input, read into inROM */
    file = fopen(argv[1], "rb");
    inROM = malloc(COMPSIZE);
    fread(inROM, COMPSIZE, 1, file);
    fclose(file);

    /* Find file table, write to fileTab */
    tabStart = findTable();
    fileTab = (uint32_t*)(inROM + tabStart);
    tab = getTableEnt(2);
fprintf(stderr, "start: 0x%08x | end: 0x%08x\n", tab.startV, tab.endV);
    tabSize = tab.endV - tab.startV;
    tabCount = tabSize / 16;
fprintf(stderr, "tabCount: %d\n", tabCount);
    /* Fill refTab with 1 for compressed, 0 otherwise */
    refTab = malloc(tabCount);
    for(i = 0; i < tabCount; i++)
    {
        tab = getTableEnt(i);
        refTab[i] = (tab.endP == 0) ? '0' : '1';
        if(tab.endP == 0xFFFFFFFF)
            refTab[i] = '0';
    }

    /* Write fileTab to table.bin */    
    file = fopen("dmaTable.dat", "w");
    fwrite(refTab, tabCount, 1, file);
    fclose(file);
    free(inROM);
    free(refTab);
    
    return(0);
}

uint32_t findTable()
{
    uint32_t i;
    uint32_t* tempROM;

    tempROM = (uint32_t*)inROM;

    for(i = 1048; i+4 < UINTSIZE; i += 4)
    {
        if(tempROM[i] == 0x00000000)
            if(tempROM[i+1] == 0x60100000)
                return(i * 4);
    }

    fprintf(stderr, "Error: Couldn't find dma table\n");
    exit(1);
}

table_t getTableEnt(uint32_t i)
{
    table_t tab;

    tab.startV = bSwap_32(fileTab[i*4]);
    tab.endV   = bSwap_32(fileTab[(i*4)+1]);
    tab.startP = bSwap_32(fileTab[(i*4)+2]);
    tab.endP   = bSwap_32(fileTab[(i*4)+3]);

    return(tab);
}

void errorCheck(int argc, char** argv)
{
    int i;
    FILE* file;

    /* Check for arguments */
    if(argc != 2)
    {
        fprintf(stderr, "Usage: %s [Input ROM]\n", argv[0]);
        exit(1);
    }

    /* Check that input ROM exists */
    file = fopen(argv[1], "rb");
    if(file == NULL)
    {
        perror(argv[1]);
        exit(1);
    }

    /* Check that input ROM is correct size */
    fseek(file, 0, SEEK_END);
    i = ftell(file);
    fclose(file);
    if(i != COMPSIZE)
    {
        fprintf(stderr, "Warning: Invalid input ROM size\n");
        exit(1);
    }
}
