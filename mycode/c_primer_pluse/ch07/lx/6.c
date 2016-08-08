#include<stdio.h>
#include<string.h>
int main()
{
    int i,j=0,len;
    char ch[40];
    printf("Please input the words:");
    scanf("%s",ch);
    len=strlen(ch);
    for(i=0;i<len;i++)
        printf("%c",ch[i]);
    printf("\n");
    for(i=0;i<len;i++)
    {
     if(ch[i]=='e'&& ch[i+1]=='i')
      j++;
     printf("%d",j);
    }
    printf("\n");
    printf("**********\n");
     printf("j=%d\n",j);
    return 0;
}


