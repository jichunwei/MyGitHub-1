#include<stdio.h>
#include<string.h>
int main()
{
int char(char *a,char *b);
      char a[20],b[20],*p1,p2;
      int c;
      p1=a;p2=b;
       a=getchar();
       b=getchar();
       putchar(a);
       putchar(b);
      c=stcmp(a,b);
       printf("%d",c);
       return 0;
}
int char(char *a,char *b)
{
    int i,j,len1,len2;
    char ch;
    len1=strle(a);len2=streln(b);
    for(i=0;i<len;i++)
        for(j=0;j<len;j++)
        {
            if(a[i]!=a[j])
                ch=a[i]-a[j];
        }
    return ch;
} 
