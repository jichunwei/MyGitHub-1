#include<stdio.h>
#include<string.h>
int main()
{
    char name[40];
    printf("what's your name:");
    scanf("%s",name);
    printf("%s  %d ",name,strlen(name));
    return 0;
}
