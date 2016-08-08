#include <netdb.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc ,char **argv)
{
    if(argc < 2){
        fprintf(stderr,"usage:%s #port\n",argv[0]);
        exit(1);
    }
    char *bip = "172.16.255.255";
//    char *bip = "172.16.8.240";
    int port = atoi(argv[1]);
    int sockfd = socket(AF_INET,SOCK_DGRAM,0);
    int so_broadcast = 1;//
    if(sockfd < 0){
        perror("socket");
        exit(1);
    }
    setsockopt(sockfd,SOL_SOCKET,SO_BROADCAST,&so_broadcast,sizeof(so_broadcast));
    struct sockaddr_in saddr;
    memset(&saddr,0,sizeof(saddr));
    saddr.sin_family = AF_INET;
    saddr.sin_port = htons(port);
    inet_pton(AF_INET,bip,&saddr.sin_addr.s_addr);
    printf("i will broadcast:hello,xuhong sb\n");
    char *s = "hello";
    if(sendto(sockfd,s,strlen(s)*sizeof(char),0,(struct sockaddr*)&saddr,sizeof(saddr) ) < 0){
        perror("sendto");
    }else{
        printf("send success\n");
    }
    close(sockfd);
    exit(0);
}
