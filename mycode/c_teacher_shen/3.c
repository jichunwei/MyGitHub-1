#include<stdio.h>
struct Student
{
    int num; char name[20];float score; };
int main()
{ struct Student s[5]={{10101,"zhang",78},
    {10103,"wang",98.9},
    {10106,"li",98},
    {10108,"ling",76.2},
    {10110,"fun",100}
                        };
struct Student t;
int i,j,k;
for(i=0;i<4;i++)
{
    k=i;
    for(j=i+1;j<5;j++)
        if(s[j].score>s[k].score) k=j;
    t=s[i];s[i]=s[k];s[k]=t;
}
printf("Result:\n");
for(i=0;i<5;i++)
printf("%5d,%10s,%6.2f\n",s[i].num,s[i].name,s[i].score);

return 0;
}
    
