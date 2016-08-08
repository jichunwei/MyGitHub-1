#include <netdb.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "chat_msg.h"

int getipbyname(char *hostname)
{
    struct hostent *h;
    while((h = gethostent()) != NULL){
        if(!strcmp(h->h_name,hostname)){
            int ip = *((int*)h->h_addr_list[0]);
            return  ip;
        }else{
            int i = 0;
            while(h->h_aliases[i]  != NULL){
                if(!strcmp(h->h_aliases[i],hostname)){
                    int ip = *((int*)h->h_addr_list[0]);
                    return ip;
                }
                i++;
            }
        }
    }
    return 0;
}

int main(int argc,char *argv[])
{
    if(argc < 3){
        fprintf(stderr,"-usage:%s ip #port\n",argv[1]);
        exit(1);
    }
    int sockfd  = socket(AF_INET,SOCK_STREAM,0);
    if(sockfd < 0){
        perror("socket");
        exit(1);
    }
    struct sockaddr_in saddr;
    memset (&saddr,0,sizeof(saddr));
    saddr.sin_family = AF_INET;
    saddr.sin_port = ntohs(atoi(argv[2]));
    if((saddr.sin_addr.s_addr = getipbyname(argv[1])) == 0){
        inet_pton(AF_INET,argv[1],&saddr.sin_addr.s_addr);
    }else{
        char ip[16];
        memset(ip,0,16);
        inet_ntop(AF_INET,&saddr.sin_addr.s_addr,ip, 16);
        printf("ip:%s\n",ip);
    }
    //建立连接，conect()是服务器的地址和端口
    if(connect(sockfd,(struct sockaddr*)&saddr,sizeof(saddr)) < 0){
        perror("connect");
        exit(1);
    }
    ssize_t size;
    char *prompt = "send:";
    ssize_t prompt_len = strlen(prompt)*sizeof(char);
    MSG m;
    while(1){
        //客户机打印发送信息提示：send:
        write(STDOUT_FILENO,prompt,prompt_len);
        memset(&m,0,sizeof(m));
        //客户机从键盘读入数据
        size = read(STDIN_FILENO,m.msg,BUFFER_LEN);
        m.msg[size-1] = 0;
        if(size <0){
            perror("read");
        }else if(size == 0){
            break;
        }else {
            if(!strcmp("exit",m.msg)){
                break;
            }
            struct sockaddr_in caddr;
            socklen_t cddr_len = sizeof(caddr);
            //获取自己的地址和端口
            getsockname(sockfd,(struct sockaddr*)&caddr, &cddr_len);
            //发送前把网络地址转换为字符串，端口转换为整数,存入MSG(信息)中。
            inet_ntop(AF_INET,&caddr.sin_addr.s_addr,m.ip,16);
            m.port = ntohs(caddr.sin_port);
            m.delimiter = '\n';
            //发送信息给服务器
            if(write(sockfd,&m,sizeof(m)) != sizeof(m)){
                perror("write networK");
            }
            memset(&m,0,sizeof(m));
            //读取来自服务器返回的信息。
            size = read(sockfd,&m,sizeof(m));
            if(size < 0)
            {
                perror("read");
                break;
            }
            else{
//                if(is_illegal(&m,&saddr)){//如果数据合法
                    printf("%s(%d):%s\n",m.ip,m.port,m.msg);
//                }
            }
        }
    }
    close(sockfd);
}


