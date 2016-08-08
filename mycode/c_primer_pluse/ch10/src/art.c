#include <stdio.h>
#define SIZE 4

void show_a(const int *ar,int n)
{
    int i;

    for(i = 0; i < n; i++)
    {
        printf("%d",ar[i]);
    }
    printf("\n");
}

void add_a(int ar[],int n,int k)
{
    int i = 0;

    for(; i < n; i++)
    {
        ar[i] += k;
    printf("%d",ar[i]);
    }
}

int main()
{
    int a[SIZE] = { 1,2,3,4};
    
    show_a(a,SIZE);
    add_a(a,SIZE,1);
    printf("ther a afer add_a():\n");
    show_a(a,SIZE);
    return 0;
}

