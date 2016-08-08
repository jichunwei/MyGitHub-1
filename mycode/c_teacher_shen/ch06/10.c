#include<stdio.h>
int main()
{
    float aver;
    float average(float arr[],int n);
    float scores[]={71,82,63,94,75,85,77,87,33};
    aver=average(scores,10);
   printf("average=%6.2f\n",aver);
    return 0;
}
float average(float arr[], int n)
{
    float i,sum=0.0;
    for(i=0;i<n;i++)
      sum+=arr[i];
    return sum/n;   
}


