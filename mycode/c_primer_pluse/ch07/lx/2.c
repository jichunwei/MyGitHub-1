#include<stdio.h>
#include<string.h>
int main()
{
    char ch;
    int i=0;
    printf("Please input some char:");
    while((ch=getchar())!='#')
    {
        i++;
        printf("%c %d",ch,ch);
        if(i%4==0)
            printf("\n");
        if(getchar()=='\n')
            continue;
    }
    printf("\n");
    return 0;
}
