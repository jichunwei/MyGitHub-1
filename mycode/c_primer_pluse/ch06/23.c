#include<stdio.h>
#include<string.h>
int main()
{
    int i,len;
    char ch[255];
    printf("Please input some nums:");
    scanf("%s",ch);
    len= strlen(ch);
    for(i=0;i<len;i++)
    printf("%c",ch[i]);
   printf("\n"); 
    for(i=len;i>0;i--)
    printf("%c",ch[i]);
    printf("\n");
    printf("\n");
    return 0;
}
