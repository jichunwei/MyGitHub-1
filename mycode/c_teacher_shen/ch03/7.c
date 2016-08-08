#include<stdio.h>
int main()
{
    float s1,s2,s3,ave;
    int i;
    i=1;
    while (i<=5)
    {
        printf("No.%d:",i);
        scanf("%f,%f,%f",&s1,&s2,&s3);
        ave=(s1+s2+s3)/3;
        printf("%No.%d,ave=%6.2f\n",i,ave);
        i++;
    }
    return 0;
}
