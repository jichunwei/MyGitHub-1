#include <unistd.h>
#include <pwd.h>
#include <time.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/stat.h>
#include <fcntl.h>
#include "ll.h"

void f_type(S *stat)
{
    if(S_ISREG(stat->st_mode))
        printf("-");
    else if(S_ISDIR(stat->st_mode))
        printf("d");
    else if(S_ISCHR(stat->st_mode))
        printf("c");
    else if(S_ISBLK(stat->st_mode))
        printf("b");
    else if(S_ISLNK(stat->st_mode))
        printf("l");
    else if(S_ISSOCK(stat->st_mode))
        printf("s");
    else if(S_ISFIFO(stat->st_mode))
        printf("f");
    else
        printf("can find the file type mode!\n");
}

void f_mode(S *stat)
{
    if(S_IRUSR &stat->st_mode)
        printf("r");
    else
        printf("-");
    if(S_IWUSR & stat->st_mode)
        printf("w");
    else 
        printf("-");
    if(S_IXUSR & stat->st_mode)
        printf("x");
    else
        printf("-");
    if(S_ISUID & stat->st_mode)
        printf("s");
    else
        printf("-");
    if(S_IRGRP & stat->st_mode)
        printf("r");
    else
        printf("-");
    if(S_IWGRP & stat->st_mode)
        printf("w");
    else
        printf("-");
    if(S_IXGRP & stat->st_mode)
        printf("x");
    else
        printf("-");
    if(S_ISGID & stat->st_mode)
        printf("s");
    else
        printf("-");
    if(S_IROTH & stat->st_mode)
        printf("r");
    else
        printf("-");
    if(S_IWOTH & stat->st_mode)
        printf("w");
    else 
        printf("-");
    if(S_IXOTH & stat->st_mode)
        printf("x");
    else
        printf("-");
}

void f_link(S *stat)
{
    printf(" %d",stat->st_nlink);
}

void f_uname(S *stat,P *passwd)
{
    struct passwd *p;
    char buf[1024];
    memset(buf,0,1024);
  //  getpwent_r(passwd,buf,1024,&p);
    getpwnam_r(passwd->pw_name,passwd,buf,1024,&p);
    printf(" %4s",passwd->pw_name);
  //  getpwuid_r(passwd->pw_gid,passwd,buf,1024,&p);
   // printf(" %d",passwd->pw_uid);
  //  printf(" %s",p->pw_name);

}

void f_gname(S *stat,P *passwd)
{
    struct passwd *p;
    char buffer[1024];
    memset(buffer,0,1024);
    getpwnam_r(passwd->pw_name,passwd,buffer,1024,&p);
    printf(" %4s",passwd->pw_name);
 //   printf(" %d",stat->st_gid);
}

void f_size(S *stat)
{
    printf(" %5d",stat->st_size);
}

void f_time(S *stat)
{
    time_t  t = stat->st_mtime;
    struct  tm *time = localtime(&t);
    printf(" %02d-%02d %02d:%02d",time->tm_mon + 1,time->tm_mday,
            time->tm_hour,time->tm_min);
}

void f_name(char const *n)
{
    printf(" %s", n);
}

