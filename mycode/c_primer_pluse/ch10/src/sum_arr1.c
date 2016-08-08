#include <stdio.h>
#define SIZE 5

int sum(int *ar,int n)
{
    int i;
    int total = 0;
    
    for(i = 0; i < n; i++)
        total += ar[i];
    printf("the size of ar is %zd bytes.\n",sizeof ar);
}

int main()
{
    int a[SIZE] = { 10,29,2,4,2};
    int k;
    k = sum(a,SIZE);
    printf("the total numbers of a is %ld.\n",k);
    printf("the size of a is %zd bytes.\n",sizeof a);
    return 0;
}
