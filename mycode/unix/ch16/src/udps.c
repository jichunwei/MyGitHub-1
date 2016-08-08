#include <netdb.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include "server.h"

#define BUFLEN      128
#define MAXADDRLEN  256
void serve(int sockfd)
{
    int             n;
    socklen_t       alen;
    FILE            *fp;
    char            buf[BUFLEN];
    char            abuf[MAXADDRLEN];
    for(;;){
        alen = MAXADDRLEN;
        if((n = recvfrom(sockfd,buf,BUFLEN,0,(struct sockaddr *)abuf,&alen)) < 0)
        {
            perror("recvfrom");
            exit(1);
        }
        if((fp = popen("/usr/bin/uptime","r")) == NULL)
        {
            sprintf(buf,"error:%s\n",strerror(errno));
            sendto(sockfd,buf,strlen(buf),0,(struct sockaddr *)abuf,alen);
        }else{
            if(fgets(buf,BUFLEN,fp) != NULL)
                sendto(sockfd,buf,strlen(buf),0,(struct sockaddr *)abuf,alen);
            pclose(fp);
        }
    }
}

int main(int argc ,char *argv[])
{
    struct addrinfo     *ailist,*aip;
    struct addrinfo     hint;
    int                 sockfd,err,n;
    char                *host;

    if(argc != 1){
        fprintf(stderr,"usage: ruptimed");
    }
    n = HOST_NAME_MAX;
    host = malloc(n);
    if(host ==  NULL){
        perror("malloc");
        exit(1);
    }
    if(gethostname(host,n) < 0){
        perror("gethostname");
        exit(1);
    }
    hint.ai_flags = AI_CANONNAME;
    hint.ai_family = 0;
    hint.ai_socktype = 0;
    hint.ai_protocol = 0;
    hint.ai_addrlen = 0;
    hint.ai_canonname = NULL;
    hint.ai_addr = NULL;
    hint.ai_next = NULL;
    if((err = getaddrinfo(host,"ruptime",&hint,&ailist)) != 0)
    {
        perror("getaddrinfo");
    }
    for(aip = ailist; aip != NULL; aip = aip->ai_next){
        if((sockfd = initserver(SOCK_DGRAM,aip->ai_addr,aip->ai_addrlen,0)) >= 0)
        {
            serve(sockfd);
            exit(0);
        }
    }
    exit(1);
}
