#include<stdio.h>
#include<stdlib.h>
int main()
{
  FILE *fp;
  char ch, fname[10];
  printf("Please input one file name:");
  scanf("%s",fname);
  if((fp=fopen(fname,"w"))==NULL)
  {
      printf("Cannot open the file.\n");
      exit(0);
  }
   ch=getchar();
   printf("Input a string:");
   ch=getchar();
   while (ch!='#')
   {
       fputc(ch,fp);
       putchar(ch);
       ch=getchar();
   }
   fclose(fp);
   putchar(10);
   return 0;
}

          
  
