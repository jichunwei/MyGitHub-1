#include<stdio.h>
int main()
{
    void fun(int n);
    int a;
    printf("enter a num(q to quit):\n");
   while(scanf("%d",&a)==1)
   {
       printf("*********\n");
    printf("jie guo:");
    fun(a);
    putchar('\n');
    printf("enter a next num:\n");
   }
  printf("\n"); 
   return 0;
}

void fun(int n)
{
    int r;
    
        r=n%8;
    if(n>=8)
       fun(n/8);
   // putchar('0'+r);
    printf("%d",r);
} 



    
    
    
       
