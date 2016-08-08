#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

void * th_fn(void *arg)
{
    printf("0x%lx running\n",pthread_self());
    return (void*)0;
}

void out_attr(pthread_attr_t *attr)
{
    int state;
    int err;
    err = pthread_attr_getdetachstate(attr,&state);
    if( PTHREAD_CREATE_JOINABLE == state){
        printf("joinable\n");
    }
    if( PTHREAD_CREATE_DETACHED == state){
        printf("detached\n");
    }
}

int main()
{
    int err;
    pthread_t th;
    pthread_attr_t attr;
    pthread_attr_init(&attr);
    out_attr(&attr);
    pthread_attr_setdetachstate(&attr,PTHREAD_CREATE_DETACHED);
    if((err=pthread_create(&th,&attr,th_fn,(void*)0)) != 0){
        fprintf(stderr,"%s\n",strerror(err));
    }
    pthread_attr_destroy(&attr);
    int *r;
    if((err=pthread_join(th,(void*)r)) != 0){
        fprintf(stderr,"%s\n",strerror(err));
    }
    else {
        printf("return is %d\n",(int)r);
    }
    printf("0x%lx finished\n",pthread_self());
    exit(0);
}


    
