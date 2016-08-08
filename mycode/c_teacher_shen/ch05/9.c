#include<stdio.h>
int main()
{
    void average(float *p,int n);
    void search(float (*p)[4],int n);
    float score[3][4]={{87,34,23,66},{36,77,89,99},{88,50,88,37}};
    average(*score,12);
    search(score,2);
    return 0;
}
void average(float *p,int n)
{
    float *p_end;
    *p_end=n-1;
    float sum,ave;
    for( ;*p<n-1;*p++)
        { sum+=*p;
            ave=sum/n;
            printf("sum=%d,ave=%d\n",sum,ave);
        }
    printf("\n");
}
void search(float (*p)[4],int n)
{
    int i;
    printf("the score of No.%d:\n");
    for(i=0;i<4;i++)
   printf("%d\n",*(*(p+2)+i));
   printf("\n");
}   

           



