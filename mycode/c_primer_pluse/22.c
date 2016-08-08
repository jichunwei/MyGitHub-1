#include<stdio.h>
int main()
{
    float c;
    printf("input a number:");
    scanf("%f",&c);
    printf("the input is %2.1f or %.1e\n",c,c);
    printf("the input is %.1e\n",c);
    return 0;

}
