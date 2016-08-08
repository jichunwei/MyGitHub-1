#include<stdio.h>
void swap(int *pa, int *pb)
{
    int t;
        t=*pa;*pa=*pb;*pb=t;
        printf("pa=%o,pb=%o\n",pa,pb);
    return;
}
int main()
{
    int a,b;
    int *p1,*p2;
    printf("input a & b :",a,b);
    scanf("%d %d",&a,&b);
    p1=&a;p2=&b;
    printf("a:%d;b:%d\n",a,b);
    if(a<b)    
    swap(p1,p2);
    printf("a=%d,b=%d\n",a,b);
    printf("*p1=%d,*p2=%d\n",*p1,*p2);
    printf("&a=%o,&b=%o\n",&a,&b);
    printf("p1=%o,p2=%o\n",p1,p2);
    return 0;
}


