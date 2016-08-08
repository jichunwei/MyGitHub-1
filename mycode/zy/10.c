#include<stdio.h>
int main()
{
    int a=0,i;
    for(i=0;i<5;i++)
    {
        switch(i)
        {
            case 0:
            case 3:a+=2;
            case 1:
            case 2:a++;
            default:a+5;
        }
    }
        printf("%d\n",a);

}
