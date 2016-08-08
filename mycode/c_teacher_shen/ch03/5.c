#include<stdio.h>
void action1(int x,int y)
{
    printf("x+y=%d\n",x+y);
}
void action2(int x,int y)
{
    printf("x-y=%d\n",x-y);
}
int main()
{
    char ch;
    int a=15,b=6;
    printf("A:   x+y\n");
    printf("B:   x-y\n");
    printf("your are:");
     scanf("%c",&ch);
    switch (ch)
    {
        case 'A':
        case 'a':action1(a,b);break;
        case 'b':
        case 'B':action2(a,b);break;
        default:printf ("date error\n");break;
    }
    return 0;
}

