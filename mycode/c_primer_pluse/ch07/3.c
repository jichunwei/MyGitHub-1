#include<stdio.h>
#define PERIO '.'
int main()
{
    int ch;
    int charcount= 0;
    while((ch=getchar() != PERIO))
    {
        if(ch!='"'&& ch!='\'')
            charcount++;
    }
    printf("there are %d non-quote characters.\n",charcount);
    return 0;
}
        

