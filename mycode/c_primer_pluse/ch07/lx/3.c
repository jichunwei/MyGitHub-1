#include<stdio.h>
int main()
{
    int i,n;
    int k=0,j=0;
    int sum=0,sum1=0;
    int a[n];
    float t_ave,p_ave;
    printf("enter a nums(<=0 to quit):");
    scanf("%d",&n);
    printf("enter the numbers of a[n]:");
    for(i=0;i<n;i++)
        scanf("%d",&a[i]);
    for(i=0;i<n;i++)
        printf("%3d",a[i]);
    printf("\n");
    for(i=0;i<n;i++)
    {
        if(a[i]%2==0)
        { k++;
            sum=sum+a[i];
            t_ave=sum/k;
        }
        else
        {
            j++;
            sum1=sum1+a[i];
            p_ave=sum1/j;
        }
    }
            printf("k=%d sum=%3dt_ave=%4.2f\n",k,sum,t_ave);
            printf("j=%d sum1=%3dp_ave=%4.2f\n",j,sum1,p_ave);
        
    printf("\n");
    return 0;
}
/*    for(i=1,t=0,p=1;i<=n;i++,p+2)
    {
        t=t+2;
        p+=2;
        sum1=sum1+t;
        sum=sum+p;
    printf("sum1=%d sum=%d",sum1,sum);
    printf("\n");
        
    */
     /*   if(i%2==0)
        {
            t_ave=t/(i/2);
            p_ave=p/(i/2);
        }
        else
        {
            p_ave=p/((i+1)/2);
            t_ave=t/((i+1)/2-1);
        }
        */
        
    //    printf("t_ave=%f p_ave=%f",t_ave,p_ave);
  //  }
   //     printf("t_ave=%4.2f p_ave=%4.2f",t_ave,p_ave);
        
