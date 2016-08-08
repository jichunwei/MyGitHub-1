#include<stdio.h>
int main()
{
    int fact(int n);
    int rfact(int n);
    int num;
    
    printf("enter an num:\n");
    scanf("%d",&num);
    printf("%d %ld\n",num,fact(num));
    printf("%d %ld\n",num,rfact(num));
    return 0;
}
int fact(int n)
{
    int a,i;
    
    for(a=1,i=1;i<=n;i++)
        a*=i;
    return a;
}
int rfact(int n)
{
    int a;
    if(n>0)
        a=n*rfact(n-1);
    else
        a=1;
    return a;
}



