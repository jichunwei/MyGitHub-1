#include<stdio.h>
#define NUM ok
//#include<stdio.h>
int main()
{
    struct stu 
    {
        int num;
        char *name;
        char sex;
        float score;
    }*ps;
    ps=(struct stu*)malloc(sizeof(struct stu));
    ps->num=102;
    ps->name="zhang ping";
    ps->sex='M';
    ps->score=62.5;

#ifndef NUM
printf("Number=%d\nScore=%f\n",ps->num,ps->score);
#else
printf("Name=%s\nSex=%c\n",ps->name,ps->sex);
#endif
free(ps);
}
