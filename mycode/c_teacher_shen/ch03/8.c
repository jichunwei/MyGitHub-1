/*#include<stdio.h>
int main()
{
    int i ,n,s=0;
    printf("input a num:");
    scanf("%d",&n);
    for(i=0;i<=n;i++)
        s=s+i;
    i++;
        printf("s=%d\n",s);
        return 0;
}
*/
#include<stdio.h>
int main()
{
    int i,sum=0;
    for(i=0;i<=10;i++)
        sum=sum+i;
    i++;
    printf("%d\n",sum);
}

/*
#include<stdio.h>
int main()
{
    int i=1,sum=0;
    while (i<=10)
    {   sum=sum+i;i++;
    }
    printf("sum=%d\n",sum);
return 0; 
}
*/
/*
#include<stdio.h>
int main()
{
    int i=0,sum=0;
    do
    {
    sum=sum+i;i++;
    } while(i<=10);
    printf("sum=%d\n",sum);
    return 0;
    }
    */
