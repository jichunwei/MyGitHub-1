#include<stdio.h>
int main()
{
    int a[5]={100,200,300,400,500};
    int *p1,*p2,*p3;
    p1=a;
    p2=&a[2];
    printf("pointer value,dereferenced pointer,pointer address:\n");
    printf("p1=%p,*p1=%d,&p1=%p\n",p1,*p1,&p1);
    p3=p1+4;
    printf("\nadding an int to a pointer:\n");
    printf("p1+4=%p,*(p1+3)=%d\n",p1+4,*(p1+3));
    p1++;
    printf("\nvalues after p1++\n");
    printf("p1=%p,*p1=%d,&p1=%p\n",p1,*p1,&p1);
    p2--;
    printf("\nvalues after p2--\n");
    printf("p2=%p,*p2=%d,&p2=%p\n",p2,*p2,&p2);
    --p1;
    ++p2;
    printf("\npointers reset to original values:\n");
    printf("p1=%p,p2=%p\n",p1,p2);

    printf("\nsubtracting one pointer from anoter\n");
    printf("p2=%p,p1=%p,p2-p1=%p\n",p2,p1,p2-p1);

    printf("\nsubtracting one integer from a pointer\n");
    printf("p3=%p,p3-2=%p\n",p3,p3-2);
    return 0;
}

