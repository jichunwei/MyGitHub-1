#include<stdio.h>
#define SIZE 5
int main()
{
    void show_a(const double ar[],int n);
    void mult_a(double ar[],int n,double mult);
    double a[SIZE]={22,12.2,242,2,23.0};
    printf("the original a:\n");
    show_a(a,SIZE);
    mult_a(a,SIZE,2.5);
    printf("the a array after calling mult_a():\n");
    show_a(a,SIZE);
    return 0;
}
void show_a(const double ar[],int n)
{
    int i;
    for(i=0;i<n;i++)
        printf("%8.3f",ar[i]);
    printf("\n");
}
void mult_a(double ar[],int n,double mult)
{
    int i;
    for(i=0;i<n;i++)
    { 
        ar[i]+=mult;
    }
}



