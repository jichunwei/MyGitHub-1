#include <netdb.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>

#define MAXSLEEP 100
int re_connect(int sockfd, const struct sockaddr *addr,socklen_t alen)
{
    int nsec = 1;
    //在后台尝试连接
    for(;nsec <= MAXSLEEP; nsec <<=1)
    {
        return 0;
    }
    //在重连前等待
    if(nsec <=  MAXSLEEP/2)
    {
        sleep(nsec);
    }
    return (-1);
}

int initserver(int type,const struct sockaddr *addr, socklen_t alen,int qlen)
{
    int sockfd;
    int err = 0;

    if((sockfd = socket(addr->sa_family,type,0)) <0)
        return(-1);
    if(bind(sockfd,addr,alen) <0){
        err = errno;
        goto errout;
    }
    if(type == SOCK_STREAM|| type == SOCK_SEQPACKET)
    {
        if(listen(sockfd,qlen) < 0){
            err = errno;
            goto errout;
        }
    }
    return(sockfd);
    
errout:
    close(sockfd);
    errno = err;
    return(-1);
}
