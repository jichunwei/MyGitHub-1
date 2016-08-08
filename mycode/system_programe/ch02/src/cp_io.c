#include "mstdio.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void cp(char *src, char *dest)
{
    int ch;
    FILE *sfp = fopen(src,"r");
    if(sfp == NULL){
        perror("fopen");
        exit(1);
    }
    FILE *dfp = fopen(src,"w");
    if(dfp == NULL){
        perror("fopen");
        exit(1);
    }
    while((ch = fgetc(sfp)) != EOF){
        fputc(ch,dfp);
        }
    fclose(sfp);
    fclose(dfp);
        
}

void mcp(char *src,char *dest)
{
    int ch;
    MFILE *sfp = mfopen(src,"r");
    if(sfp == NULL){
        perror("mfopen");
        exit(1);
    }
    MFILE *dfp = mfopen(src,"w");
    if(dfp == NULL){
        perror("mfopen");
        exit(1);
    }
    
    while((ch = mfgetc(sfp)) != MEOF){
        mfputc(ch,dfp);
        }
    mfclose(sfp);
    mfclose(dfp);

}

int main(int argc, char *argv[])
{
    if (argc < 4)
    {
        fprintf(stderr,"-usage:%s src dest1 dest2\n",argv[0]);
        exit(1);
    }
    mcp(argv[1],argv[2]);
    cp(argv[1],argv[3]);
    return 0;
}

