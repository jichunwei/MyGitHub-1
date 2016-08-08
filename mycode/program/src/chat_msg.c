#include "chat_msg.h"
#include <string.h>
#include <assert.h>

//判断MSG地址和端口信息是否和发送的端口和信息一致。
int is_illegal(MSG *msg,struct sockaddr_in *addr)
{
    assert(msg != NULL);
    if((strlen(msg->ip) < 7)||(msg->delimiter != '\n'))
        return 0;
    char  buff[16];
    memset(buff,0,sizeof(buff));
    inet_ntop(AF_INET,&addr->sin_addr.s_addr,buff,16);
    unsigned short  port = ntohs(addr->sin_port);
    if((!strcmp(buff,msg->ip)) && (port == msg->port))
        return 1;
    return 0;
}

//像MSG内填入发送端的地址和端口信息，和内容
int fill_msg(MSG *m,char *ip, unsigned short port,char *msg)
{
    assert(m != NULL);
    if(strlen(ip) > 15) 
        return 0;
    strcpy(m->ip,ip);
    m->port = port;
    strcpy(m->msg,msg);
    if(strlen(m->msg) > BUFFER_LEN) 
        return 0;
    m->delimiter = '\n';
    return 1;
}


