#include <unistd.h>
#include <netdb.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "chat_msg.h"
#include <signal.h>

int sockfd;

//信号处理函数
void sig_handler(int signo)
{
    if(signo == SIGINT){
        printf("ets will exited\n");
        close (sockfd);
        exit(1);
    }
}

//获取客户端的网络地址和端口，然后打印。
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

//处理来自客户机的信息。
void do_service(int fd)
{
    MSG m;
    ssize_t size;
    while(1){
        memset(&m,0,sizeof(m));
        size = read(fd,&m,sizeof(MSG));//接受客户机的MSG
        if(size < 0){//读失败
            perror("read");
            close(fd);
            break;
        }else if(size  == 0)//客户机关闭发送,或者读完。
        {
            printf("client closed\n");
            close(fd);
            break;
        }else{//接受成功
            struct sockaddr_in paddr;
            socklen_t   paddr_len = sizeof(paddr);
            getpeername(fd,(struct sockaddr*)&paddr,&paddr_len);//获取对方的端口和网络地址
            if(is_illegal(&m,&paddr)){//调用判断，如果是合法信息。
                struct sockaddr_in saddr;
                socklen_t   saddr_len = sizeof(saddr);
                getsockname(fd,(struct sockaddr*)&saddr,&saddr_len);//获取自己的地址信息。
                char ip[16];
                memset(ip,0,sizeof(ip));
                inet_ntop(AF_INET,&saddr.sin_addr.s_addr,ip,16);//把服务器（自己）的地址存入ip[16]。
                unsigned short port = ntohs(saddr.sin_port);
                out_addr(fd);//在服务器内打印客户机的相关信息（地址，端口）
                fill_msg(&m,ip,port,m.msg);//服务器再像MSG中写入服务器的地址和端口，以及内容。
                if(write(fd,&m,sizeof(m)) != sizeof(m)){//发送回信息给客户机。
                    perror("write");
                }
            }
        }
    }
}

int main(int argc ,char *argv[])
{
    if(argc < 2){
        fprintf(stderr,"-usage:%s#port\n",argv[0]);
        exit(1);
    }
    sockfd = socket(AF_INET,SOCK_STREAM,0);//创建SOCKET
    if(sockfd < 0){
        perror("socket");
        exit(1);
    }
    //创建结构体，填入服务器地址和端口信息，网络类型。
    struct sockaddr_in saddr;
    memset(&saddr,0,sizeof(saddr));
    saddr.sin_family = AF_INET;
    saddr.sin_port = htons(atoi(argv[1]));
    saddr.sin_addr.s_addr = INADDR_ANY;
    //.邦定地址和SOCKET。
    if(bind(sockfd,(struct sockaddr*)&saddr,sizeof(saddr)) <0){
        perror("bind");
        exit(1);
    }
    //接受来自客户机的发送请求。
    if(listen(sockfd,10) < 0){
        perror("listen");
        exit(1);
    }
    //服务器捕捉到SIGINT信号，进行相关操作。
    if(signal(SIGINT,sig_handler) == SIG_ERR){
        perror("signal");
        exit(1);
    }
    while(1){
        //处理接受的请求，产生新的SOCKET，是一个5元组。
        int fd = accept (sockfd,NULL,NULL);//没有对新的SOCKET做记录
        if(fd < 0){
            perror("accept");
        }else{
            //对接受的数据，服务器进行的相关操作
            do_service(fd);
        }
    }
    exit(1);
}


