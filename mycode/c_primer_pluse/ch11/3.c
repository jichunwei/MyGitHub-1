#include<stdio.h>
int main()
{
   char heart[]="wo men de ge";
   char *head = "wo men de ge";
   int i;
   for(i=0;i<6;i++)
   putchar(heart[i]);
   putchar('\n');

   for(i=0;i<6;i++)
       putchar(head[i]);
   putchar('\n');
   
   for(i=0;i<6;i++)
       putchar(*(heart+i));
   putchar('\n');

   for(i=0;i<6;i++)
       putchar(*(head+i));
   putchar('\n');
   
   while(*(head)!='\0')
       putchar(*(head)++);
   putchar('\n');
   
}
