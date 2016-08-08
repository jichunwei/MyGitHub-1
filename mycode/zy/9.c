#include<stdio.h>
int main()
{
    int x;
    for (x=3;x<6;x++)
        printf((x%2)?"**%d":"##%d\n",x);

}   
