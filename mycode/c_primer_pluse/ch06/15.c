#include<stdio.h>
#include<string.h>
int main()
{
    char ch[40];
    int i,len,t;
    printf("please input some num:");
    scanf("%s",ch);
    len=strlen(ch);
    for(i=len;i>=0;i--)
        printf("%c",ch[i]);
    printf("\n");
/*    for(i=0;ch[i]!='\0';i++,len--)
    {
        t=ch[i];
        ch[i]=ch[len-1];
        ch[len-1]=t;
        printf("index=%d:%2c\n",i+1,ch[i]);
    }
    */
    printf("*********\n");
        printf("index=%d:%2c\n",i+1,ch[i]);
    
    printf("\n");
    return 0;
}
    



    
