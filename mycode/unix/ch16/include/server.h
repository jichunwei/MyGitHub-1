#ifndef  __SERVER_H__
#define  __SERVER_H__
#include <netdb.h>

extern int re_connect(int sockfd,const struct sockaddr *addr,socklen_t alen);
extern int initserver(int type,const struct sockaddr *addr,socklen_t alen,int qlen);
#endif
