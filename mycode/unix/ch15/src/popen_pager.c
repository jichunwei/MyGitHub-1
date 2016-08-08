#include <unistd.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>

#define PAGER "${PAGER:-more}"
#define MAXLINE 1024

int main(int argc,char *argv[])
{
    char line[MAXLINE];
    FILE *fpin,*fpout;

    if(argc != 2){
        fprintf(stderr,"-usage:%s <pathname>\n",argv[0]);
        exit(1);
    }
    if((fpin = fopen(argv[1],"r")) == NULL)
    {
        perror("fopen");
        exit(1);
    }
    if((fpout = popen("more","w")) == NULL)
  //  if((fpout = popen(PAGER,"w")) == NULL)
    {
        perror("popen");
        exit(1);
    }

    while(fgets(line,MAXLINE,fpin) != NULL){
        if(fputs(line,fpout) == EOF){
            perror("fputs");
        }
    }
    if(ferror(fpin)){
        perror("fget");
        exit(1);
    }
    if(pclose(fpout) < 0){
        perror("pclose");
        exit(1);
    }
    exit(0);
}
