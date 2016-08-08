#ifndef __LL_H__
#define __LL_H__
#include <sys/stat.h>
#include <pwd.h>

#define  P struct passwd
#define  S struct stat  
extern void f_type(S *stat);
extern void f_mode(S *);
extern void f_link(S *);
extern void f_uname(S *,P*);
extern void f_gname(S *,P*);
extern void f_size(S *);
extern void f_time(S *);
extern void f_name(char const *);
#endif
