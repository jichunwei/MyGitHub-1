#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <errno.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <netdb.h>

int     sockfd;
int     fd1;
void sig_handler(int signo)
{
    if(SIGINT == signo){
        fprintf(stderr,"interupt occured!\n");
        close(sockfd);
        exit(0);
    }
}

char *out_msg(fd1)
{
    char    buffer[1024] = "徐宏是煞笔!";

    //   while(read(sockfd,buffer,1024) > 0){
    if(write(fd1,buffer,1024) < 0){
        perror("write");
        exit(1);
    }
    //  }
    printf("\n");
}

void out_addr(int fd, struct sockaddr_in *caddr)
{
    int port = ntohs(caddr->sin_port);
    char ip[16];
    memset(ip,0,16);
    inet_ntop(AF_INET,&caddr->sin_addr.s_addr,ip,16);
    printf("client:%s(%d)\n",ip,port); char out_buf[22];
    memset(out_buf,0,22);
    sprintf(out_buf,"%15s:%5d\n",ip,port);
    write(fd,out_buf,22);
}

int main(int argc,char **argv)
{
    if(argc != 2){
        fprintf(stderr,"usage:%s #port\n",argv[1]);
        exit(1);
    }
    if(signal(SIGINT,sig_handler) == SIG_ERR){
        perror("signal");
        exit(1);
    }
    sockfd = socket(AF_INET,SOCK_STREAM,0);
    if(sockfd < 0){
        perror("socket");
        exit(1);
    }
    struct sockaddr_in      saddr;
    socklen_t                saddr_len = sizeof(saddr);
    saddr.sin_family = AF_INET;
    saddr.sin_port = htons(atoi(argv[1]));
    saddr.sin_addr.s_addr = INADDR_ANY;
    if(bind(sockfd,(struct sockaddr*)&saddr,saddr_len) < 0){
        perror("bind");
        exit(1);
    }
    if(listen(sockfd,128) < 0){
        perror("listen");
    }
    int                     fd;
    struct  sockaddr_in     caddr;
    socklen_t               caddr_len = sizeof(caddr);
    while(1){
        if((fd = accept(sockfd,(struct sockaddr*)&caddr,&caddr_len)) < 0){
            perror("accept");
            exit(1);
        }else{
            out_addr(fd,&caddr);
            out_msg(fd);
            out_msg(fd1);
        }
    }
    close(fd);
    exit(0);
}
