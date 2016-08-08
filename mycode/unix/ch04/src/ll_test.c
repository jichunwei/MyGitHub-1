#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/stat.h>
#include "ll.h"

int main(int argc,char *argv[])
{
   int      i;
   struct stat stat;
   struct passwd passwd;

   if(argc < 2){
       fprintf(stderr,"usage:%s\n",argv[0]);
       exit(1);
   }
   for(i = 1; i < argc; i++)
   {
       if(lstat(argv[i],&stat) < 0){
           perror("lstat");
           continue;
       }
       f_type(&stat);
       f_mode(&stat);
       f_link(&stat);
       f_uname(&stat,&passwd);
       f_gname(&stat,&passwd);
       f_size(&stat);
       f_time(&stat);
       f_name(argv[i]);
       printf("\n");
   }
   printf("\n");
   return 0;
}
