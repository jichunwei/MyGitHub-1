#include<stdio.h>

int main()
{
    int words=0;
    char str[81];
    int i;
    char ch;
    int num=0;
    printf("input a sistence:");
    scanf("%s",ch);
    for(i=0;(ch=str[i])!='\0';i++)
  {
      if(ch==' ')
          words=0;
      else if(words==0)
      {
          words=1; num++;
      }
  }

  printf("There are %d words in the line.\n",num);
  return 0;
}
