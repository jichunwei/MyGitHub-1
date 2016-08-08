#include <pthread.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct{
    int             counter;
    int             res;
    pthread_cond_t  cond;
    pthread_mutex_t mutex;
}Result;

void *set_fn(void *arg)
{
    int i = 1,sum = 0;
    for(; i <= 100; i++)
    {
        sum += i;
    }
    Result *r = (Result*)arg;
    r->res = sum;
    pthread_mutex_lock(&r->mutex);
    while(r->counter < 2)
    {
        pthread_mutex_unlock(&r->mutex);
        usleep(100);
        pthread_mutex_lock(&r->mutex);
    }
    pthread_mutex_unlock(&r->mutex);
    pthread_cond_broadcast(&r->cond);
    return (void*)0;
}

void *get_fn(void *arg)
{
    Result * r = (Result*)arg;
    pthread_mutex_lock(&r->mutex);
    r->counter++;
    pthread_cond_wait(&r->cond,&r->mutex);
    int res = r->res;
    pthread_mutex_unlock(&r->mutex);
    printf("0x%lx get sum is %d\n",pthread_self(),res);
    printf("sum is %d\n",res);
    return (void*)0;
}

int main()
{
    int err;
    pthread_t   cal,g1,g2;
    Result r;
    r.counter = 0;
    pthread_cond_init(&r.cond,NULL);
    pthread_mutex_init(&r.mutex,NULL);
    if((err=pthread_create(&cal,NULL,set_fn,(void*)&r))!=0){
        fprintf(stderr,"%s\n",strerror(err));
    }
    if((err=pthread_create(&g1,NULL,get_fn,(void*)&r))!=0){
        fprintf(stderr,"%s\n",strerror(err));
    }
    if((err=pthread_create(&g2,NULL,get_fn,(void*)&r))!=0){
        fprintf(stderr,"%s\n",strerror(err));
    }
    pthread_join(cal,NULL);
    pthread_join(g1,NULL);
    pthread_join(g2,NULL);
    pthread_cond_destroy(&r.cond);
    pthread_mutex_destroy(&r.mutex);
    exit(0);
}

