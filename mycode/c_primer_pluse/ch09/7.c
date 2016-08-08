#include<stdio.h>
int main()
{
    int swap(int *u,int *v);
    int x=5,y=10;
    printf("x=%d y=%d\n",x,y);
    swap(&x,&y);
    printf("NOW:x=%d y=%d\n",x,y);
    return 0;
}
int swap(int *u,int *v)
{
   int t;
   t=*u;
   *u=*v;
   *v=t;
}

