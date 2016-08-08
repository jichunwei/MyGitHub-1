#include<stdio.h>
#include<stdlib.h>
int main()
{
    FILE *in,*out;
    char str[10],infile[10],outfile[10];
    int i;
    float d;
    printf("input input file name:");
    scanf("%s",infile);
    printf("input output file name:");
    scanf("%s",outfile);
    if((in=fopen(infile,"r"))==NULL)
    {
        printf("cannot open input file.\n");
        exit(0);
    }
    if((out=fopen(outfile,"w"))==NULL)
    {
        printf("cannot open output file,\n");
        exit(1);
    }
   fscanf(in,"%d, %f",&i,&d);
    while(!feof(in))
    {
 //       fscanf(in,"%d, %f",&i,&d);
        printf("%5d;%7.2f\n",i,d);
        fprintf(out,"%5d;%7.2f\n",i,d);
        fscanf(in,"%d, %f",&i,&d);
        
    }
    fclose (in);
    fclose (out);
    return 0;
}

        
