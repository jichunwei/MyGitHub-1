#ifndef __JOB_H__
#define __JOB_H__
#include <sys/types.h>
enum RedirectType{RedirectRead,RedirectWrite,RedirectAppend};

typedef struct{
    enum RedirectType redirect;
    int               fd;
}Redirection;

typedef struct{
    char    **args;
    pid_t   pid;
    Redirection *redirects;
    int    redirect_num;
}Program;

typedef struct job{
    char    *cmd;
    int     progs_num;
    Program *progs;
    pid_t   pgid;
    struct job *next;
}Job;

typedef struct{
    Job  *head;//后台JOB 连
    Job  *forejob;
}JobSet;

extern JobSet* create_jobset(void);
extern void    destroy_jobset(JobSet *set);
extern int     add_job(JobSet *set,Job *job);
extern void    set_forejob(JobSet *set,Job *job);
extern Job* create_job(char *cmd);
extern void destroy_job(Job* job);
extern Program * create_program(char **arg);
extern void desetory_program(Program *prog);
extern int  add_program(Job *job,Program *prog);
extern Redirection* create_redirect(int fd, enum RedirectType type);
extern void destroy_redirect(Redirection* r);
extern int add_redirection(Program* prog,Redirection *r);

#endif

