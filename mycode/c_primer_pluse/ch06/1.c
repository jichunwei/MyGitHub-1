#include<stdio.h>
int  main()
{
    long num;
    long sum=0L;
    int status;

    printf("please enter an integer to be summed:");
    printf("(q to quit):");
    status=scanf("%1d",&num);
    while(status ==1)
    {
        sum=sum+num;
        printf("please enter next number(q to quit):");
    status=scanf("%1d",&num);
    }
    printf("those integers sum to %1d.\n",sum);
    return 0;
}
        
