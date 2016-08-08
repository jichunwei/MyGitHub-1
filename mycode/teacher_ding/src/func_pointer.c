#include <stdio.h>
#include<malloc.h>
void fun1(int *i,int *j)
{
    i = (int *) malloc(sizeof(int));
    * i = 0;
}
int main()
{
    int i = 3;
    int j = 5;
    fun1(&i,&j);
    printf("i is %d\n",i);
    return 0;
}
