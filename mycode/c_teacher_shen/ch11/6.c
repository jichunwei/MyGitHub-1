#include<stdio.h>
#include<stdlib.h>
int main()
{
    FILE *fp;
    char fname[10];
    int i,n;
    printf("input n:");
    scanf("%d",&n);
    printf("input a file name:");
    scanf("%s",fname);
    if((fp=fopen(fname,"w"))==NULL)
    {
        printf("can not open the file.\n");
        exit(0);
    }
    for(i=0;i<n;i++)
    {
        fprintf(fp,"%3d,%6.2f\n",i+200,i+78.5);
    }
    fclose(fp);
    return 0;
}
    



