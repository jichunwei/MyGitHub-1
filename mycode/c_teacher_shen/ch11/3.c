#include<stdio.h>
#include<stdlib.h>
int main()
{
    FILE *in,*out;
    char ch,infile[10],outfile[10];
    printf("Input input file name:");
    scanf("%s",infile);
    printf("Input out file name:");
    scanf("%s",outfile);
    if((in=fopen(infile,"r"))==NULL)
    {
        printf("cannot open input file .\n");
        exit(0);
    } 
    if((out=fopen(outfile,"a"))==NULL)
    {
        printf("cannot open output file.\n");
        exit(0);
    }
    while((ch=fgetc(in))!=EOF)
    {
        fputc(ch,out);
        putchar(ch);
    }
    fclose(in);fclose(out);putchar(10);
    return 0;

}
        
      
            


