#include<stdio.h>
float MAX=0, MIN=0;
int  main()
{
 float    av(float array[],int n);
        float ave,score[10];
    int i;
    printf("please enter 10 scores:\n");
    for (i=0;i<10;i++)
        scanf("%f",&score[i]);
    ave=av(score,10);
    printf("MAX=%6.2f\nMIN=%6.2f\naverage=%6.2f\n",MAX,MIN,ave);
    return 0;
}
float av(float array[],int n)
{
    int i;float aver,sum=array[0];
    MAX=MIN=array[0];
    for(i=0;i<n;i++)
    {
        if(array[i]>MAX) MAX=array[i];
        else if(array[i]<MIN) MIN=array[i];
        sum=sum+array[i];
    }
    aver=sum/n;
    return(aver);
}
