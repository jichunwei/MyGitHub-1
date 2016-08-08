#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <setjmp.h>

int g_v;
jmp_buf env;

void f1(int g_v,int s_v,int a_v,int r_v,int m_v,int v_v);

void f2();
int main()
{
    static int s_v;
    int a_v;
    register r_v;
    int *m_v = (int *)malloc(sizeof(int));
    volatile int v_v;
    g_v = 1; s_v = 2;a_v = 3; r_v = 4; *m_v = 5;
    v_v = 6;
    int k = 0;
    if(k = setjmp(env) < 0)
    {
        perror("setjmp");
    }
    else if(1 == k)
    {
        printf("after longjmp\n");
        printf("global %d,static %d,auto %d,reg %d,heap %d, vola %d\n",
                g_v,s_v,a_v,r_v,*m_v,v_v);
        exit(0);
    }
    g_v = 10; s_v = 20;a_v = 30; r_v = 40; *m_v = 50;
    v_v = 60;
    f1( g_v,s_v,a_v,r_v,*m_v,v_v);
    return 0;
}

void f1(int g_v,int s_v,int a_v,int r_v,int m_v,int v_v)
{
    printf("before longjmp\n");
    printf("global %d,static %d,auto %d,reg %d,heap %d, vola %d\n",
                g_v,s_v,a_v,r_v,m_v,v_v);
    f2();
}

void f2()
{
    longjmp(env, 1);
}



