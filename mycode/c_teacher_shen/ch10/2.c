#include<stdio.h>
struct
{
    int num;
    char name[10];
    char sex;
    char job;
    union{
        int class;
        char position[10];
    }category;
}person[2];
int main() 
{
    int i;
    for(i=0;i<2;i++)
        {
        scanf("%s %d %c %c",&person[i].name,person[i].num,
                &person[i].sex,&person[i].job);
        if(person[i].job=='s')
            scanf("%d",&person[i].category.class);
        else if(person[i].job=='t')
            scanf("%s",person[i].category.position);
        else 
            printf("Input error!\n");
        }
    printf("\n");

for(i=0;i<2;i++)
{
    if(person[i].job=='s')
        printf("%-6s%-10d%-4s%-4c%-10d\n",person[i].name,person[i].num,
                person[i].sex,person[i].job,person[i].category.class);
    else
        printf("%-6s%-10d%-4s%-4c%-10s\n",person[i].name,person[i].num,
       person[i].sex,person[i].job,person[i].category.position);
}
return 0;
}

