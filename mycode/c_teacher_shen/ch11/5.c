#include<stdio.h>
#include<stdlib.h>
int main()
{
  FILE *in,*out;
  char str[10], infile[10],outfile[10];
  printf("Please input one file name:");
  scanf("%s",infile);
  printf("Please input output file name:");
  scanf("%s",outfile);
  if((in=fopen(infile,"r"))==NULL)
  {
      printf("Cannot open input file.\n");
      exit(0);
  }
  if((out=fopen(outfile,"w"))==NULL)
  {
      printf("Cannot open output file.\n");
      exit(0);
  }

  while(fgets(str,10,in)!=NULL)
  {
   fputs(str,out);
   printf("%s",str);
  }
   fclose(in);
   fclose(out);
   putchar(10);
   return 0;
}

          
  
