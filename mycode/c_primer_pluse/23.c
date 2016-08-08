#include<stdio.h>
int main()
{
    float c;
    char name[20];
    printf("what's your name:");
    scanf("%s",name);
   printf("what's your hight:");
   scanf("%f",&c);
   printf("%s you are %0.3f feet tall\n",name,c);
   return 0;
}


