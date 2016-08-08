#ifndef __IO_H__
#define __IO_H__
#include <sys/types.h>
extern void copy(int infd,int outfd);
extern void set_f1(int fd, int flag);
extern void clr_f1(int fd, int flag);
extern int lock_reg(int fd, int cmd, int type, off_t offset,short whence,off_t length);
extern pid_t lock_test(int fd,short type,off_t offset,short whence,off_t length);

#define READ_LOCKW(fd,offset,whence,length) lock_reg(fd,F_SETLKW,F_RDLCK,offset,whence,length)
#define READ_LOCK(fd,offset,whence,length) \
    lock_reg(fd,F_SETLK,F_RDLCK,offset,whence,length)
#define WRITE_LOCK(fd,offset,whence,length) \
    lock_reg(fd,F_SETLK,F_WRLCK,offset,whence,length)
#define WRITE_LOCKW(fd,offset,whence,length) \
    lock_reg(fd,F_SETLKW,F_WRLCK,offset,whence,length)
#define UNLOCK(fd,offset,whence,length) \
    lock_reg(fd,F_SETLK,F_UNLCK,offset,whence,length)
    
#endif
