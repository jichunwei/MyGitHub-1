#include<stdio.h>
int main()
{
    char name1[11],name2[11];
    int count;
    printf("please input two name.\n");
    count=scanf("%5s %10s",name1,name2);
    printf("I read %d names %s and %s.\n",count ,name1,name2);
    return 0;
}
