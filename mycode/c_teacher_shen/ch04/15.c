#include<stdio.h>
#include<string.h>
int main()
{
    int i,j,len,ok;
    char s[100];
    printf("enter some words:");
    scanf("%s",s);
    len=strlen(s);
    for(i=1;i<len;i++)
    {
        if(len%i!=0) continue;
        ok=1;
        for(j=1;j<len;j++)
        {
            if(s[j]!=s[j%i]) {ok=0;break;}
        }
        printf("%d",ok);
        if(ok==1)
        {
            printf("%d\n",i);
        }
        }
    return 0;
} 
