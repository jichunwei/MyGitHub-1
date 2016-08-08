#ifndef __CHAT_MSG__
#define __CHAT_MSG__

#define BUFFER_LEN   1024
typedef struct {
    char                ip[16];
    unsigned short      port;
    char                delimiter;
    char                msg[BUFFER_LEN];
}MSG;

extern int is_illegal(MSG *msg,struct sockaddr_in* addr);
extern int is_fillmsg(MSG *m,char *ip, unsigned short port,char *msg);
#endif
