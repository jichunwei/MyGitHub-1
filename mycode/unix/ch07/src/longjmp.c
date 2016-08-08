#include <stdlib.h>
#include <setjmp.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>

static int  g_v;
static  jmp_buf jmp;

void f2();
void f1(int g_v,int a_v,int r_v,int s_v, int v_v)
{
    printf("in f1():\n");
    printf("g_v = %d,a_v = %d,r_v = %d,s_v = %d,v_v = %d\n",g_v,a_v,r_v,s_v,v_v);
    f2();
}

void f2()
{
    longjmp(jmp,1);
}

int main()
{
    int                 a_v;
    register int        r_v;
    static int          s_v;
    volatile int        v_v;

    a_v = 1,r_v = 2,s_v = 3,v_v = 4,g_v = 5;

    if(setjmp(jmp) != 0){
        printf("after longjmp:\n");
        printf("g_v:%d,a_v:%d,r_v:%d,s_v:%d,v_v:%d\n",g_v,a_v,r_v,s_v,v_v);
        exit(0);
    }

    a_v = 10,r_v = 20,s_v = 30,v_v = 40,g_v = 50;
    f1(g_v,a_v,r_v,s_v,v_v);
    exit(0);
}
