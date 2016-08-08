#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <signal.h>
#include <unistd.h>

int main(int argc,char *argv[])
{   
    int sockfd = socket(AF_INET,SOCK_STREAM,0);
    if(sockfd < 0){
        perror("socket");
        exit(1);
    }
    struct sockaddr_in saddr;
    memset(&saddr,0,sizeof(saddr));
    saddr.sin_family = AF_INET;
    saddr.sin_port = htons(atoi(argv[1]));
    saddr.sin_addr.s_addr = 0; 
    if(bind(sockfd,(struct sockaddr*)&saddr,sizeof(saddr)) < 0){
        perror("bind");
        exit(1);
    }
    if(listen(sockfd,1) < 0){
        perror("listen");
        exit(1);
    }
    struct  sockaddr_in caddr;
    socklen_t   caddr_len = sizeof(caddr);
    int fd;
    if(fd = accept(sockfd,(struct sockaddr*)&caddr,&caddr_len) < 0){
        perror("accept");
        kill(SIGINT,getpid());
    }
    char buffer[16];
    int port = ntohs(caddr.sin_port);
    memset(buffer,0,sizeof(buffer));
    inet_ntop(AF_INET,caddr.sin_addr.s_addr,buffer,16);
    printf("client:%s(%d)\n",buffer,port);
    char out_buff[22];
    memset(out_buff,0,sizeof(out_buff));
    sprintf(out_buff,"%s:%d",buffer,port);
    write(fd,out_buff,22);
    char buff[1024];
    memset(buff,0,1024);
    ssize_t size;
    while(1){
        if(size = read(fd,buff,1024) < 0){
             perror("read");
        }
        else if(size == 0){
            break;
        }else 
            write(STDOUT_FILENO,buff,size);
    }
    close(fd);
    exit(0);
}


