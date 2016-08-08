#include<stdio.h>
int main()
{
    void to_binary(int n,int p);
    int  a,b,c;
    printf("Enter tow integers(q to quit):\n");
    while(scanf("%d%d",&a,&b)==2)
    {
       // printf("binary equivalent:");
        printf("jie guo:");
        to_binary(a,b);
        putchar('\n');
        printf("Enter an  interger(q to quit):\n");
    }
    printf("\n");
    return 0;
}
void to_binary(int n,int p)
{
    int r;
    r=n%p;
    if(n>=p)
        to_binary(n/p,p);
    putchar('0'+r);
//    return;
}



