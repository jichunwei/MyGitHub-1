#include<stdio.h>
int main()
{
/*    struct Student
        {
            long int num;    

            char name[20];
            char sex;
            char addr[20];
        }a={10101,"Li Lin",'M',
            "123 Beijing Road"};
    printf("No.:%ld\nname:%s\nsex:%c\nadderess:%s\n", a.num,a.name,a.sex,a.addr);
    return 0;
    */
    struct student 
    {
        long int num;
        char name[20];
        char sex;
        char addr[20];
    };
    struct student a = {
        10101;
       "li lin";
       'M';
       "beijing";
    };
    printf("No.:%ld\nname:%s\nsex:%c\nadderess:%s\n", a.num,a.name,a.sex,a.addr);
   return 0; 
}
