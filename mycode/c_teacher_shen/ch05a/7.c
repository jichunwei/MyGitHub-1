#include<stdio.h>
int main(int agrc,char *agrv[])
{
    while(agrc>1)
    {
        agrv++;
        printf("%s",*agrv);
        agrc--;
    }
    return 0;
}
                
