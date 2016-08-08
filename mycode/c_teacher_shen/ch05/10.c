#include<stdio.h>
int main()
{
    void searcher(float (*p)[4],int n);
    float a[3][4]={{88,66,77,77},{33,55,66,78},{77,77,66,77}};
        searcher(a,3);
    return 0;
}
void searcher(float (*p)[4],int n)
{
    int i,j,flag;
    for(i=0;i<n;i++)
    {
        flag=0;
        for(j=0;j<4;j++)
            if(p[i][j]<60)
            {flag=1;break;}
        if(flag)
        {  printf("No.%d:",i);
            for(j=0;j<4;j++)
                printf("%7.2f",p[i][j]);
            printf("\n");
        }
    }
} 
    
