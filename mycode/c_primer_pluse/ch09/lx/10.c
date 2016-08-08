#include<stdio.h>
int main()
{
    void to_binary(int n);
    int  a;
    printf("Enter a integers(q to quit):\n");
    while(scanf("%d",&a)==1)
    {
       // printf("binary equivalent:");
        printf("jie guo:");
        to_binary(a);
        putchar('\n');
        printf("Enter an  interger(q to quit):\n");
    }
    printf("\n");
    return 0;
}
void to_binary(int n)
{
    int r;
    r=n%8;
    if(n>=8)
        to_binary(n/8);
    putchar('0'+r);
//    return;
}



