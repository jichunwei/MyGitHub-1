#include<stdio.h>
int main()
{
    int a1[4][2]={{2,3},{3,4},{2,5},{3,5}};
    int (*a)[2];
    a=a1;
    
    printf("a=%p,a+1=%p\n",a,a+1);
    printf("&a[0]=%p,a[0]+1=%p\n",&a[0],a[0]+1);
    printf("*a=%p,*a+1=%p\n",*a,*a+1);
    printf("a[0][0]=%d\n",a[0][0]);
    printf("*a[0]=%d\n",*a[0]);
    printf("**a=%d\n",**a);
    printf("a[2][1]=%d\n",a[2][1]);
    printf("*(*(a+2)+1)=%d\n",*(*(a+2)+1));
    printf("*(*a+2)+1=%d\n",*(*a+2)+1);
     return 0;
}


