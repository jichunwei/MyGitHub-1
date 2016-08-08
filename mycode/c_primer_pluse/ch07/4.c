#include<stdio.h>
int main()
{
    int a,b;
/*    printf("enter a:");
    while(scanf("%d",&a)==1)
    {
     printf("a=%d\n",a);
     printf("enter b:");
     if(scanf("%d",&b)==1)
     printf("b=%d\n",b);
     printf("s=%d\n",a*b);
     printf("enter next a:");
    }
    */
    printf("enter a & b:");
    while(scanf("%d %d ",&a,&b)==2)
    {
        printf("a=%d\n",a);
        printf("b=%d\n",b);
        printf("s=%d\n",a*b);
    }
    printf("done!\n");
    return 0;
}

        
