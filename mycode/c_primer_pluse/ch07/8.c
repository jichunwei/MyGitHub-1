#include<stdio.h>
int main()
{
void display(char cr,int lines,int width);
    int ch;
    int rows,cols;
    printf("enter a characte and ntwo intergers:\n");
    while((ch=getchar())!='\n')
    {
        if(scanf("%d %d",&rows,&cols)!=2)
            break;
        display(ch,rows,cols);
        while(getchar()!='\n')
            continue;
        printf("enter another character and two intergers:\n");
        printf("enter an newline to quit\n" );
    }
    printf("bye\n");
    return 0;
}
void display(char cr,int lines,int width)
{
    int row,col;
    for(row=1;row<=lines;row++)
    {
        for(col=1;col<=width;col++)
            putchar(cr);
        putchar('\n');
    }
}


