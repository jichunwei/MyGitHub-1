#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <pwd.h>

#define MAXSIZE     1024

int main(int argc, char *argv[])
{
    int     k;
    int     i = 1;
    struct passwd passwd;
    struct passwd *p;
    char buffer[MAXSIZE];

    if(argc < 2){
        fprintf(stderr,"usage:%s\n",argv[0]);
        exit(1);
    }        
    memset(buffer,0,MAXSIZE);
    for(;i < argc; i++)
    {
        if((k = getpwent_r(&passwd,buffer,MAXSIZE,&p)) < 0){
            perror("getpwent");
        }
        printf("%s:%s:%d:%d::%s:",passwd.pw_name,passwd.pw_passwd,passwd.pw_uid,passwd.pw_gid,
                passwd.pw_gecos);
        printf("%s:%s\n",passwd.pw_dir,passwd.pw_shell);
    }
    printf("\n");
    return 0;
}

