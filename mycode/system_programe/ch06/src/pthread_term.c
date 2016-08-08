#include  <pthread.h>
#include  <stdio.h>
#include  <stdlib.h>
#include  <string.h>
#include  <errno.h>

void term_func(void *arg)
{
    char *s = (char*)arg;
    printf("term_func:%s\n",s);

}

void* th_fn_ret(void *arg)
{
    int execute = (int)arg;
    pthread_cleanup_push(term_func,"ret first calling");
    pthread_cleanup_push(term_func,"ret second calling");
    printf("return from thread\n");
    pthread_cleanup_pop(execute);
    pthread_cleanup_pop(execute);
    return (void*)0;

}

void *th_fn_exit(void *arg)
{
    int execute = (int)arg;
    pthread_cleanup_push(term_func,"exit first calling");
    pthread_cleanup_push(term_func,"exit second calling");
    printf("exit from thread\n");
    pthread_cleanup_pop(execute);
    pthread_cleanup_pop(execute);
    pthread_exit((void*)0);
}

int main()
{
    int err;
    pthread_t th;
    printf("return from thread and execute is 0\n");
    if((err=pthread_create(&th,NULL,th_fn_ret,(void*)0))!= 0){
        fprintf(stderr,"%s\n",strerror(err));
    }
    pthread_join(th,NULL);
    printf("return from thread and execute is 1\n");
    if((err=pthread_create(&th,NULL,th_fn_ret,(void*)1))!= 0){
        fprintf(stderr,"%s\n",strerror(err));
    }
    pthread_join(th,NULL);
    printf("return from thread and execute is 0\n");
    if((err=pthread_create(&th,NULL,th_fn_exit,(void*)0)) != 0){
        fprintf(stderr,"%s\n",strerror(err));
    }
    pthread_join(th,NULL);
    printf("return from thread and execute is 1\n");
    if((err=pthread_create(&th,NULL,th_fn_exit,(void*)1)) != 0){
        fprintf(stderr,"%s\n",strerror(err));
    }
    pthread_join(th,NULL);
    return 0;
}


