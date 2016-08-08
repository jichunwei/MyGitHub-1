#include <netdb.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include "server.h"

#define BUFLEN 128
#define QLEN    10

#ifndef HOST_NAME_MAX
#define HOST_NAME_MAX 256
#endif

void server(int sockfd)
{
    int clfd;
    FILE *fp;
    char buf[BUFLEN];

    for(;;){
        clfd = accept(sockfd,NULL,NULL);
        if(clfd < 0){
            perror("clfd");
            exit(1);
        }
        if((fp = popen("/usr/bin/uptime","r")) == NULL){
            sprintf(buf,"error: %s\n",strerror(errno));
            send(clfd,buf,strlen(buf),0);
        }else{
            while(fgets(buf,BUFLEN,fp) != NULL)
                send(clfd,buf,strlen(buf),0);
            pclose(fp);
        }
        close(clfd);
    }
}

int main(int argc,char **argv)
{
    struct addrinfo *ailist ,*aip;
    struct addrinfo  hint;
    int     sockfd,err,n;
    char    *host;

    if(argc != 1)
    {
        printf("usage:ruptimed\n");
    }
#ifdef _SC_HOST_NAME_MAX
    n = sysconf(_SC_HOST_NAME_MAX);
    if(n < 0)
#endif
    n = HOST_NAME_MAX;
    if(host = malloc(n))
         perror("malloc");
    if(gethostname(host ,n))
        perror("gethsotname");
   // daemonize("ruptimed");
    hint.ai_flags = AI_CANONNAME;
    hint.ai_family = 0;
    hint.ai_socktype = 0;
    hint.ai_addrlen = 0;
    hint.ai_protocol = 0;
    hint.ai_addr = NULL;
    hint.ai_next = NULL;
    hint.ai_canonname = NULL;
    if((err = getaddrinfo(host,"ruptime",&hint,&ailist)) != 0){
        perror("getaddrinfo");
    }
    for(aip = ailist; aip != NULL; aip = aip->ai_next){
        if((sockfd = initserver(SOCK_STREAM,aip->ai_addr,aip->ai_addrlen,QLEN)) >= 0){
            server(sockfd);
        }
    }
    exit(1);
}
    

        


        


    

