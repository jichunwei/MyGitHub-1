#include<stdio.h>
int main()
{
    void check(int *);
    int i,n,*p1;
    
  //  printf("please input data:");
   // scanf("%d",&n);
    //    for(i=0;i<n;i++)
   //         printf("tek

    p1=(int *)malloc(5*sizeof(int));
    for(i=0;i<5;i++)
        scanf("%d",p1+1);
    check(p1);
    return 0;
}
void check(int *p)
{
   
    int i;
    for(i=0;i<5;i++)
    {
        if(*p+i<60)
        { printf("the %d grade of No.%d:"p[i],i);}
    printf("\n");
}
}
