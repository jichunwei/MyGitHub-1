#include<stdio.h>
int main()
{
    char ch;
    int i,j;
    for(i=0;i<6;i++)
        {  for(ch='F',j=0;j<=i;ch--,j++)
      printf("%c",ch);
    printf("\n");
    }
    return 0;
    }

