#include<stdio.h>
int main()
{
    int j;
    float b=0, i=1;
    float sum=0;
    for(j=0;j<20;j++,i*=2.0)
    {  
        sum+=1/i;
    printf("No.%d:%f\n",j,sum);
    }
    return 0;
}
