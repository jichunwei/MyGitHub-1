#include<stdio.h>
int main()
{
    int i;
    char c;
    for(i=0;(c=getchar())!='\n';)
            if (c >'0'&& c <='9')
            i++;
            printf("i=%d\n",i);
            return 0;
        
} 
