#include<stdio.h>
#include<stdlib.h>
struct Student
{
    char name[20];
    int num;
    int  age;
    char addr[15];
    float score;
};
int main()
{
    FILE *in,*out;
    int i;
    printf("input the input file:");
    scanf("%d",&inname);
    printf("input the output file:");
    scanf("%d",&outname);
    if((in=fopen(intfile,"r"))==NULL)
    {
         printf("cann't open in file");
    exit(0);
    }
    if((out=(outfiel,"w"))==NULL)
    {
        printf("cann't open out file");
    exit(0);
    }
    







    
        
     
    
    

