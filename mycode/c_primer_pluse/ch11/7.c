#include<stdio.h>
int main()
{
    char line[81];
//    while(gets(line))
 //       puts(line);
   while(fgets(line ,81, stdin))
        puts(line);
       
     //   fputs(line ,stdout);
}
