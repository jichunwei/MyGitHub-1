#include<stdio.h>

int p=15,q=20;
int f1(int a)
{
    int b=35;
    printf("p+q=%d\n",p+q);
    printf("a+b=%d\n",a+b);
    return 0;
}
    char c1='A';
    char f2(char c)
    {
        printf("p+q=%d\n",p+q);
        printf("c1=%c,c=%c\n",c1,c);
        return c+3;
    }
int main()
    { 
        int a=100, b=200;
       printf("a+b=%d\n",a+b);
       printf("f1=%d\n",f1(b));
               printf("f2=%d\n",f2(a));
       return 0;
    }

    
