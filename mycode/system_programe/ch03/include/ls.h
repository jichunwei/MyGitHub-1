#ifndef __LS_H__
#define __LS_H__
#include <sys/types.h>
//#include <sys/stat.h>

#define S struct stat

extern void f_mode(S *);
extern void f_permission(S *);
extern void f_link(S *);
extern void f_uid(S *);
extern void f_gid(S *);
extern void f_size(S *);
extern void f_mtime(S *);
extern void f_name(char const *);
#endif




