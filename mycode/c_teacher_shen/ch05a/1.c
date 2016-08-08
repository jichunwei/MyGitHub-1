#include<stdio.h>
int main()
{
    int max(int a,int b);
    int min(int a,int b);
    int sum(int a,int b);
//    int switch(int n);
    int (*p)(int,int);

   // p=max;
    int a,b,c,d;
    printf("please input num:");
    scanf("%d %d %d",&a,&b,&c);
   
    if(c==1){ p=max;d=max(a,b);printf("max=%d\n",d);}
    if(c==2) {p=min;d=min(a,b);printf("min=%d\n",d);}
    if(c==3) { p=sum;d=sum(a,b);printf("sum=%d\n",d);}
//   c=(*p)(a,b);
 //   printf("max=%d\n",c);
 //   p=min;
  //  c=(*p)(a,b);
   // printf("min=%d\n",c);
   //   switch(1);printf("%d\n",max(a,b));
    //  switch(2);printf("%d\n",min(a,b));
    //  switch(3);printf("%d\n",sum(a,b));
    return 0;
}
int max(int a,int b)
{
    int c;
    return(c=(a>b)?a:b);
}
int min(int a,int b)
{
    return(a<b?a:b);
}
int sum(int a,int b)
{
    return (a+b);
}
/*int switch(int n)
{
    int n;
    int a,b;
    switch(n)
    {
    case 1:max(a,b);break;return max;
    case 2:min(a,b);break;return min;
    case 3:sum(a,b);break;return sum;
    case 4:printf("data error\n");break;
    }
}
*/

    
   
