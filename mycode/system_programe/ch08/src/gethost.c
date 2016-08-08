#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <memory.h>

void out_adr(struct hostent *h)
{
    printf("hostname:%s\n",h->h_name);
    printf("addrtype:%s\n",h->h_addrtype == AF_INET?"ipv4":"ipv6");
    char ip[16];
    memset(ip,0,16);
    inet_ntop(h->h_addrtype,h->h_addr_list[0],ip,16);
    printf("ip address:%s\n",ip);
}

int main(int argc,char **argv)
{
    if(argc < 2){
        fprintf(stderr,"usage:%s host\n",argv[0]);
        exit(1);
    }
    struct hostent *h;
    while((h = gethostent()) != NULL){
        if(!strcmp(argv[1],h->h_name)){
            out_adr(h);
            exit(0);
        }
        else{
            int i = 0;
            while(h->h_aliases[i] != NULL){
                if(!strcmp(argv[1],h->h_aliases[i])){
                    out_adr(h);
                    exit(0);
                }
                i++;
            }
        }
    }
    endhostent();
    printf("no %s exist\n",argv[1]);
}

