#ifndef __CHAT_MSG__
#define __CHAT_MSG__
#include <netdb.h>
#define BUFFER_LEN 1024

typedef struct {//服务器和客户机共同遵循的协议
    char                    ip[16];
    unsigned short          port;
    char                    delimiter;//分隔符为换行。
    char                    msg[BUFFER_LEN];//发送端信息
}MSG;

//判断MSG地址和端口是否和服务器接受的地址和端口信息一致
extern int  is_illegal(MSG *msg,struct sockaddr_in *addr);
//像接受过来的MSG内填写接收端的地址和端口，以及内容
extern int  fill_msg(MSG *m,char *ip,unsigned short port,char *msg);

#endif
