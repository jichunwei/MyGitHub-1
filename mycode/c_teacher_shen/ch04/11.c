#include<stdio.h>
#include<string.h>
int main()
{
    char ch[20]="people";
    char ch1[]="China";
    printf("%s\n",strcat (ch,ch1));
    strcpy(ch,ch1);
    printf("%s\n",ch);
    strcpy(ch,ch1);
    puts(ch);
    return 0;
}


