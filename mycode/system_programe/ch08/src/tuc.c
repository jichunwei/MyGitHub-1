#include <netdb.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <memory.h>

int main(int argc,char **argv)
{
    if(argc < 3){
        fprintf(stderr,"usage:%s ip #port\n",argv[0]);
        exit(1);
    }
    //1,construct the socket
    int sockfd = socket(AF_INET,SOCK_DGRAM,0);
    if(sockfd <0){
        perror("socket");
        exit(1);
    }
    //2.construct the address
    struct sockaddr_in saddr;
    memset(&saddr,0,sizeof(saddr));
    saddr.sin_family = AF_INET;
    saddr.sin_port = htons(atoi(argv[2]));
    inet_pton(AF_INET,argv[1],&saddr.sin_addr.s_addr);
    //3.set default desetination
    if(connect(sockfd,(struct sockaddr*)&saddr,sizeof(saddr)) < 0){
        perror("connect");
    }
    //4,send data to default destination
    char b[1024];
    if(send (sockfd,b,1,0) < 0){
        perror("send");
    }
    memset(b,0,sizeof(b));
    if(recv(sockfd,b,sizeof(b),0) <0){
        perror("recv");
    }else {
        printf("time :%s\n",b);
    }
    close(sockfd);
    exit(0);
}

