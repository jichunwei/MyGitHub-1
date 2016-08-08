#include <unistd.h>
#include <netdb.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "chat_msg.h"
#include <signal.h>
#include <pthread.h>

int sockfd;

void sig_handler(int signo)
{
    if(signo == SIGINT){
        printf("ets will exited\n");
        close (sockfd);
        exit(1);
    }
}

void out_addr(int fd)
{
    struct sockaddr_in caddr;
    socklen_t   cddr_len = sizeof(caddr);
    getpeername(fd,(struct sockaddr*)&caddr,&cddr_len);
    char ip[16];
    int port;
    memset(ip,0,16);
    inet_ntop(AF_INET,&caddr.sin_addr.s_addr,ip,16);
    port = ntohs(caddr.sin_port);
    printf("msg from %s(%d)\n",ip,port);
}

void do_service(int fd)
{
    MSG m;
    ssize_t size;
    while(1){
    memset(&m,0,sizeof(m));
    size = read(fd,&m,sizeof(MSG));
    if(size < 0){
        perror("read");
        close(fd);
        break;
    }else if(size  == 0)
    {
        printf("client closed\n");
        close(fd);
        break;
    }else{
        struct sockaddr_in paddr;
        socklen_t   paddr_len = sizeof(paddr);
        getpeername(fd,(struct sockaddr*)&paddr,&paddr_len);
        if(is_illegal(&m,&paddr)){
            struct sockaddr_in saddr;
            socklen_t   saddr_len = sizeof(saddr);
            getsockname(fd,(struct sockaddr*)&saddr,&saddr_len);
            char ip[16];
            memset(ip,0,sizeof(ip));
            inet_ntop(AF_INET,&saddr.sin_addr.s_addr,ip,16);
            unsigned short port = ntohs(saddr.sin_port);
            out_addr(fd);
            fill_msg(&m,ip,port,m.msg);
            if(write(fd,&m,sizeof(m)) != sizeof(m)){
                perror("write");
            }
        }
    }
    }
}

void* service_fn(void *arg)
{
    int fd = (int )arg;
    do_service(fd);
    return (void*)0;
}

int main(int argc ,char *argv[])
{
    if(argc < 2){
        fprintf(stderr,"-usage:%s#port\n",argv[0]);
        exit(1);
    }
    sockfd = socket(AF_INET,SOCK_STREAM,0);
    if(sockfd < 0){
        perror("socket");
        exit(1);
    }
    int err;
    pthread_t th;
    pthread_attr_t attr;
    pthread_attr_init(&attr);
    pthread_attr_setdetachstate(&attr,PTHREAD_CREATE_DETACHED);

    struct sockaddr_in saddr;
    memset(&saddr,0,sizeof(saddr));
    saddr.sin_family = AF_INET;
    saddr.sin_port = htons(atoi(argv[1]));
    saddr.sin_addr.s_addr = INADDR_ANY;
    if(bind(sockfd,(struct sockaddr*)&saddr,sizeof(saddr)) <0){
        perror("bind");
        exit(1);
    }
    if(listen(sockfd,10) < 0){
        perror("listen");
        exit(1);
    }
    if(signal(SIGINT,sig_handler) == SIG_ERR){
        perror("signal");
        exit(1);
    }
    while(1){
        int fd = accept (sockfd,NULL,NULL);
        if(fd < 0){
            perror("accept");
        }else{
            err = pthread_create(&th,&attr,service_fn,(void*)fd);
            if(err != 0){
                fprintf(stderr,"-usage:%s\n",strerror(err));
            }
        }
    }
    exit(1);
}


