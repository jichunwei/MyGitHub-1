#include <netdb.h>
#include <time.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <memory.h>
#include <signal.h>
#include <pthread.h>
#include "vector_fd.h"
#include <sys/types.h>

VectorFD  *vfd;
int sockfd;

void sig_handler(int signo)
{
    if(SIGINT == signo){
        printf("server will be exited\n");
        close(sockfd);
        destroy_vector_fd(vfd);
        exit(0);
    }

}

void do_service(int fd)
{
    char    buffer[1024];
    size_t  size;
    memset(buffer,0,1024);
    size = read(fd,buffer,1024);
    if(size == 0){
        printf("client closed\n");
        remove_fd(vfd,fd);
        close(fd);
    }else if(size  > 0){
        if(write(fd,buffer,size) != size){
            perror("write");
            remove_fd(vfd,fd);
            close(fd);
        }
        if(write(STDOUT_FILENO,buffer,size) != size){
            perror("write");
        }
    }
}

int add_set(fd_set *set)
{
    FD_ZERO(set);
    int max_fd = vfd->fd[0];
    int i = 0;
    for(; i < vfd->counter; i++){
        if(get_fd(vfd,i) > max_fd)
        max_fd = get_fd(vfd,i);
        FD_SET(get_fd(vfd,i) ,set);
    }
    return max_fd;
}

void* service_fn(void *arg)
{
    struct timeval t;
    t.tv_sec = 2;
    t.tv_usec = 0;
    int n = 0;
    int max_fd;
    fd_set set;
    max_fd = add_set(&set); 
    while((n = select(max_fd+1,&set,NULL,NULL,&t)) >= 0){
        if(n > 0){
            int i = 0;
            for(; i < vfd->counter;i++){
                if(FD_ISSET(get_fd(vfd,i),&set)){
                    do_service(get_fd(vfd,i));
                }
            }
        }
        t.tv_sec = 2;
        t.tv_usec = 0;
        max_fd = add_set(&set);
    }
    return (void*)0;
}

void out_addr(struct sockaddr_in *caddr)
{
    char ip[16];
    int  port = ntohs(caddr->sin_port);
    memset(ip,0,16);
    inet_ntop(AF_INET,&caddr->sin_addr.s_addr,ip,16);
    printf("%s(%d) connected\n",ip,port);
}

int main(int argc,char **argv)
{
    if(argc < 2){
        fprintf(stderr,"-usage:%s#port\n",argv[0]);
        exit(1);
    }
    if(signal(SIGINT,sig_handler) == SIG_ERR){
        perror("signal");
        exit(1);
    }
    vfd = create_vector_fd();
    pthread_t th;
    pthread_attr_t th_attr;
    int err;
    pthread_attr_init(&th_attr);
    pthread_attr_setdetachstate(&th_attr,PTHREAD_CREATE_DETACHED);
    sockfd = socket(AF_INET,SOCK_STREAM,0);
    if(sockfd <0){
        perror("socket");
        exit(1);
    }
    struct sockaddr_in  saddr;
    memset(&saddr,0,sizeof(saddr));
    saddr.sin_family = AF_INET;
    saddr.sin_port = htons(atoi(argv[1]));
    saddr.sin_addr.s_addr = INADDR_ANY;
    if(bind(sockfd,(struct sockaddr*)&saddr,sizeof(saddr)) < 0){
        perror("bind");
        exit(1);
    }
    if(listen (sockfd,10) < 0){
        perror("listen");
        exit(1);
    }
    err = pthread_create(&th,&th_attr,service_fn,(void*)0);
    if(err != 0){
        fprintf(stderr,"%s\n",strerror(err));
        exit(1);
    }
    pthread_attr_destroy(&th_attr);
    struct sockaddr_in caddr;
    socklen_t caddr_len = sizeof(caddr);
    while(1){
        int fd = accept(sockfd,(struct sockaddr*)&caddr,&caddr_len);
        if(fd < 0){
            perror("accept");
        }else{
            out_addr(&caddr);
            add_fd(vfd,fd);
        }
    }
    exit(0);
}
