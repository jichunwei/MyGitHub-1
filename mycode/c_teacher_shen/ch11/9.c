#include<stdio.h>
#include<stdlib.h>
//#define SIZE 10
struct Student
{
    char name[10];
    int num;
    int age;
    char addr[15];
    float score;
};    
int main()
{
    FILE *fp;
    char fname[10];
    int i;
    struct Student stu;
//    printf("input n:");
 //   scanf("%d",&n);
    printf("input a file name:");
    scanf("%s",fname);
    if((fp=fopen(fname,"rb"))==NULL)
    {
        printf("Cannot open the file.\n");
        exit(0);
    }
    fread(&stu,sizeof(struct Student),1,fp);
    while(!feof(fp))
    {
        printf("%-10s,%5d,%3d,%15s,%6.2f\n",
                stu.name,stu.num,stu.age,stu.addr,stu.score);
        fread(&stu,sizeof(struct Student),1,fp);
    }
    
 /*   for(i=0;i<n;i++)
    {
    
        printf("name num age addr score :\n");
        scanf("%s %d %d %s %f",stu.name,&stu.num,&stu.age,stu.addr,&stu.score);
        s[0]=stu;
        j=i;
        while(s[j].score > stu.score)
        {
            s[j+1] = s[j]; 
            j--;
        }
        s[j+1]=stu;
    }

        
    for(i=1;i<=n;i++)
        if(fwrite(&s[i],sizeof(struct Student),1,fp)!=1)
            printf("File werite error!\n");
    */
    fclose(fp);
    return 0;
}
    
    

