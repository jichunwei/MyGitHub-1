#include<stdio.h>
#include<string.h>
struct Person{
    char name[20];
    int count;
}leader[3]={"li",0,"zhang",0,"wang",0};

int main()
{
    int i,j;
    char name[20];
    for(i=0;i<10;i++)
    {scanf("%s",name);
        for(j=0;j<3;j++)
          if(strcmp(name,leader[j].name)==0) leader[j].count++;
    }
    printf("\nResult:\n");
    for(i=0;i<3;i++)
        printf("%20s,%d\n",leader[i].name,leader[i].count);
    return 0;
}
                 

