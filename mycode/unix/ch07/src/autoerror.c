#include <stdio.h>

#define DATAFILE "datafile"
#define BUFSIZE     1024

FILE *open_data()
{
    FILE    *fp;
    char    data[BUFSIZE];

    if((fp = fopen(DATAFILE,"r")) == NULL){
        perror("fopen");
    }
    if(setvbuf(fp,data,_IOLBF,BUFSIZE) != 0)
        return NULL;
    return(fp);
}
