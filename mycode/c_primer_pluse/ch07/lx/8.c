#include<stdio.h>
int main()
{
    int i,a,n;
    for(i=0;i<70;i++)
    printf("*");
    printf("\n");
    printf("enter tehe number corresponding to the desired pay rate or action\n");
    printf("(1)$8.75/hr        ");printf("(2)$9.33/hr           ");
    printf("\n");
    printf("(3)$10.00/hr       ");printf("(4)$11.20/hr           ");
    printf("\n");
    for(i=0;i<70;i++)
        printf("*");
    printf("\n");
    printf("enter two num:");
    scanf("%d%d",&a,&n);
    while((a=scanf("%d",&a))==1)
    {
        switch(a)
        {
            case 1:printf("$%f\n",8.75*n);break;
            case 2:printf("$%f\n",9.33*n);break;
            case 3:printf("$%f\n",10.00*n);break;
            case 4:printf("$%f\n",11.20*n);break;
            default:printf("date error!");
        }

        printf("\n");
    }
        return 0;
}

