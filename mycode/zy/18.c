#include<stdio.h>
int main()
/*{
    int i;
     for( i=0;i<=100;i++)
     { 
        if (i%3==0) continue;
     printf("%10d",i);
     } 
     printf("\n");
}
*/
{
    int i=0;
while(i<=100)
{
    i++;
    if(i%3==0) continue;
    printf("%10d",i);
}
printf("\n");
}
