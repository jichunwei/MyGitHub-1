#include<stdio.h>
#include<string.h>
int main()
{
    void sort (char *name[],int n);
    void print(char *name[],int n);
    char *name[]={"tan","shi","xiong","womendege"};
    int n=4;
    sort(name ,n);
    print(name,n);
    return 0;

}
void sort(char *name[],int n)
{
    float *t;
    int i,j;
    for(i=0;i<n-1;i++)
    {
        for(j=0;j<i+1;j++)
        {
            if(strcmp(name[j],name[j+1])>0)
            {t=name[j];
                name[j]=name[j+1];
                name[j+1]=t;}
        }
    }
}                
void print(char *name[],int n)
{
    int i;
 //   char* *p;
    for(i=0;i<n;i++)
  //      p=name+i;
        printf("%s\n",name[i]);
}

