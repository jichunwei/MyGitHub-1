#include <stdio.h>
#define SIZE 4

int main()
{
    int a = 22;
    int arr[SIZE];
    int b = 23;
    int i;

    printf("a = %d, b = %d\n",a,b);
    for(i = -1; i <= SIZE; i++)
        arr[i] = 2 * i + 1;
    for(i =  -1; i <= 7; i++)
        printf("%2d %d\n",i,arr[i]);
    printf("a = %d ,b =  %d\n",a,b);

    return 0;
}

