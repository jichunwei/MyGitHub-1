#include<stdio.h>
//#define SIZE 30
int chline(char ,int,int);
int main()
{
    int i,j;
    int a;
    char ch;
    printf("Please input ch&i&j:");
    scanf("%d %d %c",&i,&j,&ch);
    chline(ch,i,j);
    return 0;
}
int chline(char ch,int a,int b)
{
    int i;
    for(i=a;i<=b;i++)
      //  printf("%c",ch);
        putchar(ch);
    printf("\n");
}


