#include<stdio.h>
int main()
{
    void hanoi(int n,char ,char ,char );
    int m;
    printf("the number of diskes:");
    scanf("%d",&m);
    printf("move %d diskes:\n",m);
    hanoi(m,'A','B','C');
    printf("end.\n");
    return 0;
}
void move(int n,char a,char b)
{
printf("disk %d: %c-->%c\n",n,a,b);
}

void hanoi(int n,char a,char b,char c)
{
    if(n==1) move (n,a,c);
    else
    {
    hanoi(n-1,a,c,b);
    move(n,a,c);
    hanoi(n-1,b,a,c);
    }
}


