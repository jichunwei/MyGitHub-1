#include<stdio.h>
int main()
{
    char ch;
    while((ch= getchar()!='#'))
    {
        if(ch=='\n');
        continue;
        printf("step 1\n");
         if(ch=='c');
        continue;
         else if(ch=='b')
            break;
         else  if(ch=='q')
            goto laststep;
        printf("step 2\n");
laststep:printf("step 3\n");
    }
    printf("done\n");
    return 0;
}

          

        
