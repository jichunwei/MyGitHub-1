#include<stdio.h>
int main()
{
    int i,num;
    int true=1;
    printf("please input the num(<=0 to quit && q to quit):\n");
    while((scanf("%d",&num)!=0))
    {
            for(i=2;i*i<=num;i++)
            {
                if(num%i==0)
                {
                    if(i*i!=num)
            printf("%d is divisible by %d and %d.\n",num,i,num/i);
                
                else 
                    printf("%d is divisible by %d\n",num ,i);
                true=0;
                }

            }
            if(true)
                printf("%2d is prime.\n",num);
            printf("enter another integer for ananlyis: ");
            printf("enter q to quit:\n");
    }
    printf("bye!\n");
   return 0;
}
           
    
