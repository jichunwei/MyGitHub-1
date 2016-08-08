#include<stdio.h>
int main()
{
    int p,q;
    scanf("%d",&p);
    while(p > 0)
    {
        printf("p=%d\n",p);
        scanf("%d",&q);
        while(q > 0)
        {
            printf("q=%d\n",q);
            printf("%d\n",p*q);
            if(q>100)
                break;
            scanf("%d",&q);
        }
        if(q>100)
            break;
        scanf("%d",&p);
    }
    return 0;
}
        
