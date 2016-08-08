#include<stdio.h>
#include<stdlib.h>
int main()
{
  FILE *fp;
  char str[10], fname[10];
  int i,n;
  printf("input the n:");
  scanf("%d",&n);
  printf("Please input one file name:");
  scanf("%s",fname);
  if((fp=fopen(fname,"w"))==NULL)
  {
      printf("Cannot open the file.\n");
      exit(0);
  }
  for(i=0;i<n;i++)
  {
      scanf("%s",str);
      fputs(str,fp);
      fputs("\n",fp);
      printf("%s\n",str);
  }
   fclose(fp);
   putchar(10);
   return 0;
}

          
  
