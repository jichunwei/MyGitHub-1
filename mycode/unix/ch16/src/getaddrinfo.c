//将主机名字和服务名字映射到一个地址
#include <stdio.h>
#include <netdb.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>

#if defined(BSD) || defined(MACOS)
#include <sys/socket.h>
#include <netinet/in.h>
#endif

#define INET_ADDRLEN  1024
//打印网络类型的名字
void print_family(struct addrinfo *aip)
{
    printf("family ");
    switch(aip->ai_family){
        case AF_INET:
            printf("inet");
            break;
        case AF_INET6:
            printf("inet6");
            break;
        case AF_UNIX:
            printf("unix");
            break;
        case AF_UNSPEC:
            printf("unspecified");
            break;
        default:
            printf("unknown");
    }
}

//打印socket的类型
void print_type(struct addrinfo *aip)
{
    printf(" type ");
    switch(aip->ai_socktype){
        case SOCK_STREAM:
            printf("stream");
            break;
        case  SOCK_DGRAM:
            printf("dgram");
            break;
        case SOCK_SEQPACKET:
            printf("seqpacket");
            break;
        case SOCK_RAW:
            printf("ram");
            break;
        default:
            printf("unknown (%d)",aip->ai_socktype);
    }
}

//打印的协议的类型
void print_protocol(struct addrinfo *aip)
{
    printf(" protocol ");
    switch(aip->ai_protocol){
        case 0:
            printf("default");
            break;
        case IPPROTO_TCP:
            printf("TCP");
            break;
        case IPPROTO_UDP:
            printf("UDP");
            break;
        case IPPROTO_RAW:
            printf("RAW");
            break;
        default:
            printf("UNKNOW protocol(%d)\n",aip->ai_protocol);
    }
}

//如何处理地址和名字
void print_flags(struct addrinfo *aip)
{
    printf(" flags ");
    switch(aip->ai_flags){
        if(aip->ai_flags == 0){
            printf("0");
        }else {
            if(aip->ai_flags & AI_PASSIVE)
                printf("passive");//socket用于监听邦定
            if(aip->ai_flags & AI_CANONNAME)//socket 用于规范名
                printf("canon");
            if(aip->ai_flags & AI_NUMERICHOST)//以数字格式返回主机地址
                printf("numerichost");
#if defined (AI_NUMERICSERV)
            if(aip->ai_flags & AI_NUMERICSERV)//以端口号返回服务
                printf("numser");
#endif
#if defined (AI_V4MAPPED)
            if(aip->ai_flags & AI_V4MAPPED)//如果没找到IP_V6,则返回IP_V6格式的ip_v4
                printf("v4mapped");
#endif
#if defined(AI_ALL)
            if(aip->ai_flags & AI_ALL)//查找ip_v4和ip_v6的地址
                printf("AI_ALL");
#endif
        }
    }
}

int main(int argc,char *argv[])
{
    struct addrinfo     *ailist,  *aip;
    struct addrinfo     hint;
    struct sockaddr_in  *saddr;
    const   char        *addr;
    int                 err;
    char                buff[INET_ADDRLEN];

    if(argc != 3){
        fprintf(stderr,"-usage:%s nodename service\n",argv[0]);
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

    if((err = getaddrinfo(argv[1],argv[2],&hint,&ailist)) != 0){
        perror("getaddrinfo");
        exit(1);
    }
    for(aip = ailist; aip != NULL; aip = aip->ai_next)
    {
        print_flags(aip);
        print_family(aip);
        print_type(aip);
        print_protocol(aip);
        printf("\n\thost %s",aip->ai_canonname?aip->ai_canonname:"-");
        if(aip->ai_family == AF_INET){
            saddr = (struct sockaddr_in *)aip->ai_addr;
            memset(buff,0,INET_ADDRLEN);
            addr = inet_ntop(AF_INET,&saddr->sin_addr.s_addr,buff,INET_ADDRLEN);
            printf(" address %s",addr?addr:"unknown");
            printf(" port %d",ntohs(saddr->sin_port));
        }
        printf("\n");
    }
    return 0;
}

