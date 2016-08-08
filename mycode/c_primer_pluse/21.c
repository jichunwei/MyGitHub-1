#include<stdio.h>
int main()
{
    char name[40];
    printf("Please input your name:");
    scanf("%s",name);
    printf("\"%-20s\" is you name\n",name);
}
