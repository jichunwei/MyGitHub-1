#include<stdio.h>
#include<string.h>
int main()
{
    char sp[] = "\t\v\\\0wi||\n";
    printf("%d\n",strlen(sp));
    return 0;
}
