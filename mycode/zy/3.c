#include<stdio.h>
int main()
{
    int a=1,b=0;
    switch(a)
    {
        case 1:
            switch(b)
            {
                case 0:printf("**0**");break;
                case 1:printf("**1**");break;
            }
        case 2:printf("**2**");break;

    }
}
