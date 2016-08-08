#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>

#define DEF_PAGER "/bin/more"
#define MAXLEN 1024

int main(int argc,char *argv[])
{
    int             fd[2];
    ssize_t         size;
    pid_t           pid;
    char            buffer[MAXLEN];
    char            *pager,*argv0;
    FILE            *fp;

    if(argc != 2){
        fprintf(stderr,"-usage:%s <pathname>\n",argv[0]);
        exit(1);
    }
    if((fp = fopen(argv[1],"r")) == NULL){
        perror("fopen");
        exit(1);
    }
    if(pipe(fd) < 0){
        perror("pipe");
        exit(1);
    }
    pid = fork();
    if(pid < 0){
        perror("fork");
    }else if(pid > 0){
        close(fd[0]);
        memset(buffer,0,MAXLEN);
        while(fgets(buffer,MAXLEN,fp) != NULL){
            size = strlen(buffer);
            if(write(fd[1],buffer,size) != size){
                perror("write");
                exit(1);
            }
        }
        if(ferror(fp)){
            perror("fgets");
        }
        close(fd[1]);
        wait(NULL);
        exit(0);
    }else{
        close(fd[1]);
        if(fd[0] != 0){
            if(dup2(fd[0],0) != 0){
                perror("dup2");
            }
            close(fd[0]);
        }
        if((pager = getenv("PAGER")) == NULL){//查找PAGER，找不到，返回系统默认
            pager = DEF_PAGER;
        if((argv0 = strrchr(pager,'/')) != NULL)//返回一个指针，指向'/'最后出现的位置
            argv0++;
        else 
            argv0 = pager;
        if(execl(pager,argv0,(char*)0) < 0){
            perror("execl");
            exit(127);
        }
        }
    }
    exit(0);
}
