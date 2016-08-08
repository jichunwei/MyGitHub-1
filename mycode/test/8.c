#include<stdio.h>
#include<string.h>
int main()
{
    char s1[] = "12345", *s2="1234";
    printf("%d\n",strlen(strcpy(s1,s2)));
    
    return 0;
}
