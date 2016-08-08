#include<stdio.h>
int main()
{
    int i=0,j=0;
    char ch;
    printf("please input some nums:");
    while((ch=getchar())!='#')
    {
        if(ch=='.')
        {
            i++;
            putchar(ch-13);
//        printf("i=%d",i);
        }
        if(ch=='!')
        {
            j++;
            putchar(ch);
            putchar(ch);
//        printf("j=%d",j);
        }
        else
            putchar(ch);
    printf("i+j=%d\n",i+j);
    }
    return 0;
}
