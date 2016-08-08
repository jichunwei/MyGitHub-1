#include <netdb.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>

int sockfd;

void sig_handler(int signo)
{
    if(signo == SIGINT){
        printf("receiver will exited\n");
        close(sockfd);
        exit(1);
    }
}

int main(int argc, char **argv)
{
    if(argc < 2){
        fprintf(stderr,"-usage:%s #port \n",argv[0]);
        exit(1);
        }
    sockfd = socket(AF_INET,SOCK_DGRAM,0);
    if(sockfd < 0){
        perror("socket");
        exit(1);
    }
    struct sockaddr_in saddr;
    memset(&saddr,0,sizeof(saddr));
    saddr.sin_family = AF_INET;
    saddr.sin_port = htons(atoi(argv[1]));
    saddr.sin_addr.s_addr = INADDR_ANY;
    if(bind(sockfd,(struct sockaddr*)&saddr,sizeof(saddr)) < 0){
        perror("bind");
        exit(1);
    }
    char buffer[1024];
    struct sockaddr_in   caddr;
    socklen_t  caddr_len = sizeof(caddr);
    while(1){
        memset(buffer,0,sizeof(buffer));
        if(recvfrom(sockfd,buffer,sizeof(buffer),0,(struct sockaddr*)&caddr,&caddr_len) < 0){
            perror("recvfrom");
        }
        char ip[16];
        int port;
        inet_ntop(AF_INET,&caddr.sin_addr.s_addr,ip,16);
        port = ntohs(caddr.sin_port);
        printf("%s(%d):%s\n",ip,port,buffer);
    }
       exit(0); 
}

