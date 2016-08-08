#include <stdio.h>
#define SIZE 4

int main()
{
    int i;
    int no_data[SIZE];

    printf("%s %18s\n","i","no_data[SIZE]");
    for(i = 0; i < SIZE; i++)
    {
        printf("%d %10d\n",i,no_data[i]);
    }
    return 0;
}



