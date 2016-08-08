#include<stdio.h>
int main()
{
    char ch;
    int i=0;
    int j=0;
    int k=0;
    printf("please input some ch:");
    while((ch=getchar())!= '#')
    {
        if(ch==' ')
         i++;
        else if(ch=='\n')
            j++;
        
        else
            k++;
    }
        printf("i=%dj=%dk=%d\n",i,j,k);
    printf("\n");
}



