#include<stdio.h>
#include<stdlib.h>
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
  //  int i;
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
    fseek(fp,-3*sizeof(struct Student),2);
    fread(&stu,sizeof(struct Student),1,fp);

    while(!feof(fp))
    {
        printf("%-10s,%5d,%3d,%15s,%6.2f\n",
                stu.name,stu.num,stu.age,stu.addr,stu.score);
      //  fseek(fp,sizeof(struct Student),1);
        fread(&stu,sizeof(struct Student),1,fp);
    }
//    for(i=1;i<=n;i++)
 //       if(fwrite(&s[i],sizeof(struct Student),1,fp)!=1)
  //          printf("File werite error!\n");
    fclose(fp);
    return 0;
}
    
    

