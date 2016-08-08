#include <stdio.h>


int* add(int i, int j)
{
    static int k;
    k = (i +j);
    return &k;

}
void thr_rn(int **p, int*  (*f)(int ,int ), int i ,int j)
{
    int *r = (*f)(i,j);
    *p = r;
}
int main()
{
    int *d;
    thr_rn( &d, add,3, 4);
    printf("result is %d\n",*d);
    return 0;
}
/*
int *add(int i, int j)
{
    static int k = i + j;
    return  &k;

}

void thr_rn(int **p, int  (*f)(int ,int ), int i ,int j)
{
    *p = (*f) (i,j);
}
int main()
{
    int *r;
    thr_rn( ...., add,3, 4);
    printf("result is %d\n",...);
    return 0;
}
*/
