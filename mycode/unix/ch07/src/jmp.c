#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <setjmp.h>

jmp_buf  jmp;

float do_cmd(int i, int j)
{
    if(j == 0)
       longjmp(jmp,1);
    return i/j;
}

int main()
{
    int a =10,b = 2,k;
    int c = 0;
    if((k = setjmp(jmp)) < 0){
        perror("setjmp");
        exit(1);
    }else if(k > 0){
        printf("j can not be zero!\n");
        exit(0);
    }
    do_cmd(a,b);
    printf("a:%d b:%d a/b:%2.00f\n",a,b,do_cmd(a,b));
    do_cmd(a,c);
    printf("a:%d c:%d a/b:%2.00f\n",a,c,do_cmd(a,c));
    exit(0);
}
