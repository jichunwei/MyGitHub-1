#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>

#define LEN 1024
void cp(int sfd,int dfd)
{
    char buff[LEN];
    ssize_t size;
    while(size = read(sfd,buff,LEN) > 0)
    {
        if(write(dfd,buff,size) != size)
        {
            perror("write");
            exit(1);
        }
        if(size < 0)
        {
            perror("read");
            exit(1);
        }
    }
}
    
int main(int argc,char *argv[])
{
    if(argc < 2)
    {
        fprintf(stderr,"-usage:%s files dir\n",argv[0]);
        exit(1);
    }
     int sfd = open(argv[1],O_RDONLY);
     int dfd = open(STDIN_FILENO,O_RDONLY);
     cp(sfd ,dfd);
     if(sfd < 0)
     {
         perror("open");
     //    exit(1);
     }
     char buffer[256];
     memset(buffer,0,256);
     if(getcwd(buffer,256) < 0)
         perror("getcwd");

     chdir(argv[2]);

     struct stat buff;
     memset(&buff,0,sizeof(buff));
     if(lstat(argv[2],&buff) < 0)
     {
         perror("lstat");
         exit(1);
     }
     if(S_ISDIR(buff.st_mode))
     {
         int fd;
         if((fd = open(argv[1],O_WRONLY|O_CREAT|O_TRUNC,0777)) < 0)
         {
             perror("open");
             exit(1);
         }
     }
     return 0;
}
             
         
             

    

 
