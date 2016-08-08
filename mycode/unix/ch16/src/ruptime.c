#include "server.h"
#include <netdb.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>
#include <unistd.h>

#define MAXADDRLEN  26   
#define BUFLEN      128

void print_uptime(int sockfd)
{
    ssize_t size;
    char buf[BUFLEN];

    while((size = recv(sockfd,buf,BUFLEN,0)) > 0)
            write(STDIN_FILENO,buf,size);
        if(size < 0)
            perror("recv");
}

int main(int argc ,char *argv[])
{
    struct addrinfo *ailist,*aip;
    struct addrinfo hint;
    int             sockfd,err;

    if(argc != 2){
        fprintf(stderr,"usage: ruptime hostname\n");
        exit(1);
    }
    hint.ai_flags = 0;
    hint.ai_family = 0;
    hint.ai_socktype = SOCK_STREAM;
    hint.ai_protocol = 0;
    hint.ai_addrlen = 0;
    hint.ai_canonname = NULL;
    hint.ai_addr = NULL;
    hint.ai_next = NULL;
    if((err = getaddrinfo(argv[1],"ruptime",&hint,&ailist)) != 0){
        perror("getaddrinfo");
    }
    for(aip = ailist; aip != NULL; aip = aip->ai_next)
    {
        if(sockfd = socket(aip->ai_family,SOCK_STREAM,0) < 0){
            perror("socket");
        }
        if(re_connect(sockfd,aip->ai_addr,aip->ai_addrlen) < 0){
            perror("re_connect");
        }else {
            print_uptime(sockfd);
            exit(0);
        }
    }
    fprintf(stderr,"can't connect to %s: %s\n",argv[1],strerror(err));
    exit(1);
}
