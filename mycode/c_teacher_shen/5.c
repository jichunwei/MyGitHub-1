#include<stdio.h>
struct Student;
{
    int num;
    float score;
    struct Student *next;
};
int main()
{
    struct Student a,b,c,*head,*p;
    a.num=10101;a.score=79;
    b.num=10103;b.score=53;
    c.num=10104;c.score=44;
    head=&a; a.next=&b;
    b.next=&c;c.next=null;
    p=head;
    do
    {
        printf("%ld%5.1f\n",p->num,p->score);
        p=p->next;
    }
    while(p!=null);
    return 0;
}
