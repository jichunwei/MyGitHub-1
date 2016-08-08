#include<stdio.h>
int main()
{
    int i;
    char a[27];
    printf("please input some char:");
    scanf("%s",a);
    for(i=0;i<26;i++)
        printf("%c",a[i]);
    printf("\n");
    return 0;
}
