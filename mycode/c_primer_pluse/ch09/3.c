#include<stdio.h>
    long fact(int n);
    long rfact(int n);
int main()
{
    int num;
   // int c,d;
    printf("this program calculates factorials\n");
    printf("enter a value in the range 0-12(q to quit):\n");
//    scanf("%d",&num);
   // c=fact(num);
  //  d=rfact(num);

 //   printf("%d %ld",num,c);
 //   printf("%d %ld",num,d);
    while(scanf("%d",&num)==1)
    {
        if(num<0)
            printf("no negative numbers,please\n");
        else if(num>12)
            printf("keep num under 13:\n");
        else
        {
            printf("loop:%d factorial = %ld\n",num,fact(num));
            printf("recursion:%d factorial =%ld\n",num,rfact(num));
        }
        printf("enter a value in the range 0-12(q to quit):\n");
    }
    
    printf("bye\n");
    return 0;
}

long fact(int n)
{
    long ans;
    for(ans=1;n>1;n--)
        ans*=n;
    return ans;
}
long rfact(int n)
{
    long ans;
    if(n>0)
        ans=n*rfact(n-1);
    else
        ans=1;
    return ans;
}
