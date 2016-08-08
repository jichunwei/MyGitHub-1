#include<stdio.h>
char f_char(char ch);
int main()
{
    char ch;
    printf("please input a num:");
    scanf("%c",&ch);
    printf("********\n");
    f_char(ch);
  //  printf("%d",f_char(ch));
   // printf("\n");
    return 0;
}
char f_char(char ch)
{
    int i,j=0;
         for(i=1,(ch='a')||(ch='A');i<=26;ch++,i++)
         {
             if((ch>='a'&&ch<='z')||(ch>='A'&&ch<='Z'))
             {
                 printf("ch=%2c i=%-3d",ch,i);
             }
             if(i%4==0)
                 printf("\n");
         }
}
            

