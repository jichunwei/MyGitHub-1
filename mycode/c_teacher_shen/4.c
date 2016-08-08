#include<stdio.h>
#define N 5
struct Student
{
    int num; char name[20];float score[3];float aver; };
int main()
{
    void input (struct Student s[],int n);
    struct Student max(struct Student s[],int n);
    void print(struct Student s);
    struct Student s[N];
    struct Student *p=s;
    input(p,N);
    print(max(p,N));
    return 0;
} 
void input (struct Student s[],int n)
{
    int i;
    for(i=0;i<n;i++)
    {
        scanf("%d%s%f%f%f",&s[i].num,s[i].name,&s[i].score[0],&s[i].score[1],&s[i].score[2]);
        s[i].aver=(s[i].score[0]+s[i].score[1]+s[i].score[2])/3;
    }
} 
struct Student max(struct Student s[],int n)
{
    int i,m=0;
    for(i=1;i<n;i++)
        if(s[m].aver<s[i].aver) m=i;
    return s[m];
}
void print(struct Student s)
{
    printf("No.:%5d;Name%10s;%5.1f;%5.1f;%5.1f;%6.2f\n",
            s.num,s.name,s.score[0],s.score[1],s.score[2],s.aver);
}


    
/*

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
*/    
