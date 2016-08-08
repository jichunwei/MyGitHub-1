#include<stdio.h>
int fun(int i,int j,char ch);
int main()
{
    char ch1;
    int a,b;
    printf("Please input two num and a word:");
    scanf("%d %d %c",&a, &b,&ch1);
    fun(a,b,ch1);
//    printf("%d %d %c",a, b,ch1);
 //   printf("\n");
    return 0;
}
int fun(int i,int j,char ch)
{
    int k;
    for(k=0;k<j;k++)
        {
            if(ch)
            printf("i=%dj=%d ch=%c\n",i,j,ch);
        }
    printf("\n");
}

    


    
 

    

   
    
