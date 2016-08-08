#include<stdio.h>
#define MIN(x,y) ((x)>(y)?(y):(x))
int main()
{
    int i=1,j=3;
    int c;
    c=MIN(i,j);
    printf("%d",c);
    printf("\n");
    return 0;
}
       
