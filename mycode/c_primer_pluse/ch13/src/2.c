#include<stdio.h>
#include<stdlib.h>
#define MAX 40
int main()
{
    FILE *fp;
    char words[MAX];

    if((fp=fopen("words","a+"))==NULL)
        {
            fprintf(stdout,"Can't open \"words\"file.\n");
            exit (1);
        }
    puts("enter words to add to the file:enter the enter");
    puts("key at the beging of a line to terminate.");
    while(gets(words)!=NULL && words[0]!='\0')
        fprintf(fp,"%s",words);
    puts("file contents:");
    rewind(fp);
    while(fscanf(fp,"%s",words)==1)
        puts(words);
        if(fclose(fp)!=0)
            fprintf(stderr,"error closling file\n");
        return 0;
}
