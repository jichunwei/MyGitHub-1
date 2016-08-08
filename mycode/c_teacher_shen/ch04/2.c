#include<stdio.h>
int main()
{
    int f[40]={1,1},i;
    for(i=2;i<40;i++)
        f[i]=f[i-1]+f[i-2];
    for(i=0;i<40;i++)
   {
      if(i%4==0) printf("\n");
        printf("%10d",f[i]);
 }
    printf("\n");
        return 0;
}
    
