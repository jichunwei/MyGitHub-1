#include<stdio.h>
#define SIZE 30
#include "sstring.h"

int strlen (char *m)
{
    int i=0;
   for(; m[i] !='\0';i++);
    printf("strlen:%d\n",i);

    return i;
}


char *strcpy (char *m,char *n)
{
    int i;

    for(i =0; i < SIZE; i++)
	m[i] = n[i];
    printf("%s\n",m);
    return m;
}

char  *strcmp (char *m,char *n)
{
    int i,j;
    for(i =0 ;m[i]!='\0';i++);
    printf("i= %d\n",i);
    for(j = 0; n[j]!= '\0'; j++);
    printf("j=%d\n",j);
    if(i>j)
    {
	printf("max is %s\n",m);
    return m;
    if(i == j)
	printf("%s is equal %s\n", m,n);
    }
    else
    {
	printf("max is %s\n",n);
    return n;
    }

}


int main()
{
    char a[SIZE],b[SIZE];
    int i,c,d;

    printf("Please input some words:\n");
    scanf("%s %s",a,b);
    *strcmp(a,b);
    printf("\n");
    printf("**********\n");
    c = strlen(a);
    d = strlen(b);
    printf("strlen(a):%d strlen(b):%d",c,d);
    printf("\n");
    *strcpy(a,b);
    printf("a= %s\n",a);

    return 0;
}
    




