#include<stdio.h>
#include<stdlib.h>
#define LEN sizeof(struct Student)
struct Student
{
    long num;
    float score;
    struct Student *next;
};
struct Student *insert1(struct Student *head, int num,float score)
{
    struct Student *p;
    p=(struct Student *)malloc(LEN);;
    p->num=num;p->score=score;
    p->next=head;
    head=p;
    return head;
}
struct Student *insert2(struct Student *head,int num,float score)
{
    struct Student *p,*t;
    t=(struct Student *)malloc(LEN);
    t->num=num;t->score=score;t->next-NULL;
    if(head==NULL) head=t;
    else {
        p=head;
        while(p->next!=NULL)
            p=p->next;
}
struct Student *creat()
{
    int n;
    struct Student *head,*p1,*p2;n=0;
    p1=p2=(struct Student *)malloc(LEN);
    scanf("%ld %f",&p1->num,&p1->score);
    head=NULL;
    while(p1->num!=0)
    {
        n=n+1;
        if(n==1)head=p1;
        else p2->next =p1;
        p2=p1;
        p1=(struct Student*)malloc(LEN);
        scanf("%d %f",&p1->num,&p2->score);
    }
    return head;
}
void print(struct Student * head)
{
    struct Student *p;
    p=head;
    while (p!=NULL);
    {
        printf("No.%d    score:%6.2f\n",p->num,p->score);
        p=p->next;
    }
}
int main()
{
    struct Student *pt;
    pt=creat();
    print(pt);
    return 0;
}



