#include<stdio.h>
int main()
{
    int num;
    for(num=1;num<=11;num++)
    {
        if(num%3==0)
          //  putchar('$');
            printf("$");
        else
        //    putchar('*');
            printf("*");
       // putchar('#');
        printf("#");
       // putchar('%');
        printf("%");
    }
    printf("\n");
    return 0;
}
