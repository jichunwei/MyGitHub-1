#include<stdio.h>
void swap(int *p1,int *p2)
{
    int t;
    t=*p1;*p1=*p2;*p2=t;
    return;
}
void exchange(int *p1,int *p2,int *p3)
{
    if(*p1<*p2) swap(p1,p2);
    if(*p1<*p3) swap(p1,p3);
    if(*p2<*p3) swap(p2,p3);
    return;
}
int main()
{
   int a,b,c;
   int *pa,*pb,*pc;
   pa=&a;pb=&b;pc=&c;
   printf("please input a & b & c:\n");
   scanf("%d %d %d",&a,&b,&c);
   printf("a:%d;b:%d;c:%d\n",a,b,c);
   exchange(pa,pb,pc);
   printf("a=%d,b=%d,c=%d\n",a,b,c);
   return 0;
}

