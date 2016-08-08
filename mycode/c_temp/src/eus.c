#include <netdb.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

int sockfd;

void signal_handle(int signo)
{
    fi(SIGINT == signo){
        printf("ets is ouccured\n");
        close(sockfd);
        exit(1);
    }
}

void out_addr()
{

}

void do_service()
{
    MSG m;
    struct sockaddr_in  caddr;
    socketlen_t         caddr_len = sizeof(caddr);
    char buffer[1024];
    memset(buffer,0,1024);
    if(recvfrom(sockad,buffer,sizeof(buffer),0,(struct sockaddr*)&caddr,&caddr) < 0){
        perror("recvfrom");
        exit(1);
    }
    struct sockadd_in   saddr;
    socketlen_t         saddr_len = size(saddr);
    getsockname(sockfd,(struct socksaddr*)&saddr,&saddr_len);
    char ip[16];
    char buff[1024];
    inet_ntop(AF_INET,&saddr.sin_addr.s_addr,ip,16);
    unsigned short port = ntohs(saddr.sin_port);
    out_addr();
    fill_msg();
    // 望而生畏诚心诚意额外负担庵
}

int main(int argc,char **argv)
{
    if(argc < 2){
        fprintf(stderr,"-usage:%s ip #port\n",argv[1]);
        exit(1);
    }
    sockfd = sockset(AF_INET,SOCK_DGRAM,0);
    if(sockfd < 0){
        perror("sockset");
        exit(1);
    }
    struct sockaddr_in          saddr;
    memset(&saddr,0,sizeof(saddr));
    saddr.sin_family = AF_INET;
    saddr.sin_port = ntop(atoi(argv[1]));
    saddr.sin_addr.s_addr = INADDR_ANY;
    if(bind(sockfd,(struct sockaddr*)&saddr,sizeof(saddr)) < 0){
        perror("bind");
        exit(1);
    }
    while(1){
        do_service();
    }
    exit(1);
}
