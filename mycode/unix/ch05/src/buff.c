#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>
#include <sys/types.h>

void pr_stdio(const char *, FILE *);

int main()
{
    FILE    *fp;
    fputs("enter any character\n",stderr);
    if(getchar() < 0){
        perror("getchar");
        exit(1);
    }
    fputs("one line to standard error\n",stderr);

    pr_stdio("stdin",stdin);
    pr_stdio("stdout",stdout);
    pr_stdio("stderr",stderr);
    
    if((fp = fopen("/etc/motd","r")) == NULL){
        perror("fopen");
    }
    if(getc(fp) < 0){
        perror("getc");
    }
    pr_stdio("/etc/motd",fp);
    exit(0);
}

void pr_stdio(const char *name, FILE *fp)
{
    printf("stream = %s, ",name);
    if(fp->_IO_file_flags & _IO_UNBUFFERED)
        printf("unbuffered");
    else if(fp->_IO_file_flags & _IO_LINE_BUF)
        printf("line bufferd");
    else 
        printf("fully buffered");
    printf(",buffer size = %d\n",fp->_IO_buf_end - fp->_IO_buf_base);
}
