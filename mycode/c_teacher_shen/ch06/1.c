#include<stdio.h>
void print_star();
void print_messge(char s[]);
int main()
{
    print_star();
    print_messge("how do you do!\n");
    print_star();
    print_messge("i am very happy!\n");
    return 0;
}
void print_star()
{
    printf("*************\n");
}
void print_messge(char s[])
{
    printf("%s\n",s);
}
