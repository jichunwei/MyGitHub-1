#include<stdio.h>
int main()
{
    char *string="i love me";
    printf("%s\n",string);
    printf("%c\n",*(string+2));
    return 0;
}
