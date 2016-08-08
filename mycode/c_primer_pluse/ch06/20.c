#include<stdio.h>
int main()
{
    int a,b,i,c;
    printf("enter a & b");
    while(scanf("%d %d",&a,&b)==1)
    {
        for(i=a;i<=b;i++)
        {
            c+=i*i;
            printf("%d\n",c);
        }
        printf("\n");
        printf("enter next a & b");
        scanf("%d %d",&a,&b);
    }
    return 0;
}
