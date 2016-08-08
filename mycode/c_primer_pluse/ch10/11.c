#include<stdio.h>
#define COLS 4
int main()
{
int sum2d(int (*ar)[COLS],int rows);
int sum(int ar[],int n);
    int t1,t2,t3;
    int *p1;
    int (*p2)[COLS];

    p1=(int [2]){10,20};
    p2=(int [2][COLS]){{1,2,3,-9},{4,5,6,-8}};

    t1=sum(p1,2);
    t2=sum2d(p2,2);
    t3=sum((int []) {4,4,4,5,5,5},6);
    printf("t1=%d\n",t1);
    printf("t2=%d\n",t2);
    printf("t3=%d\n",t3);
    return 0;
}
int sum(int ar[] ,int n)
{
    int i;
    int total=0;
    for(i=0;i<n;i++)
        total+=ar[i];
    return total;
}
int sum2d(int ar[][COLS],int rows)
{
    int r,c,tot=0;
    for(r=0;r<rows;r++)
        for(c=0;c<COLS;c++)
            tot+=ar[r][c];
    return tot;
}
