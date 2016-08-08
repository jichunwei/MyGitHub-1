#include <netdb.h>
#include <time.h>
#include <signal.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <memory.h>

int sockfd;

void sig_handler(int signo)
{
    if(signo == SIGINT)
    {
        printf("server will be exited\n");
        close (sockfd);
        exit(0);
    }
}

void out_addr(struct sockaddr_in *addr)
{
    char ip[16];
    int port;
    memset(ip,0,sizeof(ip));
    port = ntohs(addr->sin_port);
    inet_ntop(AF_INET,&addr->sin_addr.s_addr,ip,16);
    printf("client:%s(%d)\n",ip,port);
}

void do_service(void)
{
    struct sockaddr_in caddr;
    socklen_t    caddr_len = sizeof(caddr);
    char buffer[1024];
    memset(buffer,0,sizeof(buffer));
    if(recvfrom(sockfd,buffer,sizeof(buffer) ,0,(struct sockaddr*)&caddr,&caddr_len) < 0){
        perror("recvfrom");
    }else {
        out_addr(&caddr);
        long int t = time(0);
        char *ptr = ctime(&t);
        if(sendto(sockfd,ptr,strlen(ptr)*sizeof(char),0,(struct sockaddr*)&caddr,caddr_len) < 0){
            perror("sendto");
        }
    }
}


int main(int argc,char *argv[])
{
    /*
    if(argc < 2){
        fprintf(stderr,"usage:%s #port\n",argv[1]);
        exit(1);
    }
    */
    unsigned int port = htons(10000);
    struct servent *s = getservbyname("utime","udp");
    if(s != NULL){
        port = s->s_port;
    }
    printf("port:%d\n",ntohs(port));
    //1,construct the socket
    sockfd = socket(AF_INET,SOCK_DGRAM,0);
    if(sockfd < 0){
        perror("socket");
        exit(1);
    }
    //2.construct the sockaddr_in struct
    struct sockaddr_in saddr;
    memset(&saddr,0,sizeof(saddr));
    saddr.sin_family = AF_INET;
    saddr.sin_port = port;
    saddr.sin_addr.s_addr = INADDR_ANY;
    //3.bind the socket and sockaddr
    if(bind (sockfd,(struct sockaddr*)&saddr,sizeof(saddr)) < 0){
        perror("bind");
        exit(1);
    }
    if(signal(SIGINT,sig_handler) == SIG_ERR){
        perror("signal");
        exit(1);
    }
    while(1){
        //4,process the data
        do_service();
    }
    exit(1);
}
