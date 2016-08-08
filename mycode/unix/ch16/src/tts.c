#include <netdb.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <memory.h>
#include <signal.h>
#include <time.h>

int sockfd;

void sig_handler(int signo)
{
    if(SIGINT == signo){
        printf("singno is occured!\n");
        close(sockfd);
        exit(1);
    }
}

char *get_time()
{
    long int t = time(0);//获取系统当前时间。
    return ctime(&t);//把日期的时间转换为字符串。
}

void out_addr(int fd,struct sockaddr_in *caddr)
{
    int port = ntohs(caddr->sin_port);
    char buffer[16];
    memset(buffer,0,sizeof(buffer));
    inet_ntop(AF_INET,&caddr->sin_addr.s_addr,buffer,16);
    printf("client:%s(%d)\n",buffer,port);
    char out_buff[22];
    memset(out_buff,0,22);
    sprintf(out_buff,"%15s:%5d",buffer,port);
    write(fd,out_buff,22);
}

int main(int argc, char *argv[])
{
    if(argc < 2)
    {
        fprintf(stderr,"-usage:%d #port\n",argv[0]);
        exit(1);
    }
    if(signal(SIGINT,sig_handler) == SIG_ERR){
        perror("signal");
        exit(1);
    }
    //1.construct the socket
    sockfd = socket(AF_INET,SOCK_STREAM,0);
    //2.construct the sockaddr_in and fill the data
    struct sockaddr_in saddr;
    memset(&saddr,0,sizeof(saddr));
    saddr.sin_family = AF_INET;
    saddr.sin_port = htons(atoi(argv[1]));
    saddr.sin_addr.s_addr = INADDR_ANY;//ip地址系统任意分配
    //3.bind the address and socket
    if(bind(sockfd,(struct sockaddr*)&saddr,sizeof(saddr)) < 0){
        perror("bind");
        exit(1);
    }
    //4.notify the OS to accept the connection request from client
    if(listen(sockfd,10) < 0){
        perror("listen");
        exit(1);
    }
    struct sockaddr_in  caddr;
    socklen_t           caddr_len = sizeof(caddr);
    while(1){
        //5.get the client addr and port
        int fd = accept(sockfd,(struct sockaddr*)&caddr,&caddr_len);
        if(fd < 0)
        {
            perror("accept");
            kill(SIGINT,getpid());
        }
        out_addr(fd,&caddr);
        char *s = get_time();
        ssize_t size = strlen(s)*sizeof(char);
        //6,write the datea to client
        if(write(fd,s,size) != size){
            perror("write");
        }
        //7.close the connection for client
        close(fd);
    }
}

