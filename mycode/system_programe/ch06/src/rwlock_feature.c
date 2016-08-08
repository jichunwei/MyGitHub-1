#include <pthread.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

pthread_rwlock_t rwlock;

int main(int argc,char *argv[])
{
    if(argc <  3)
    {
        fprintf(stderr,"-usage:%s [r|w] [r|w]\n",argv[0]);
        exit(1);
    }
    pthread_rwlock_init(&rwlock,NULL);
    if(!strcmp("r",argv[1])){
        if(pthread_rwlock_rdlock(&rwlock) != 0){
            printf("first readlock failure\n");
        }
        else {
            printf("first readlock sucess\n");
        }
    }else if(!strcmp("w",argv[1])){
     if(pthread_rwlock_wrlock(&rwlock) != 0){
            printf("first writelock failure\n");
     }
        else {
            printf("first writelock sucess\n");
        }
    }
    if(!strcmp("r",argv[2])){
        if(pthread_rwlock_rdlock(&rwlock) != 0){
            printf("second readlock failure\n");
        }
        else {
            printf("second readlock sucess\n");
        }
    }else if(!strcmp("w",argv[1])){
     if(pthread_rwlock_wrlock(&rwlock) != 0){
            printf("first writelock failure\n");
     }
        else {
            printf("first writelock sucess\n");
        }
    }else if(!strcmp("w",argv[2])){
     if(pthread_rwlock_wrlock(&rwlock) != 0){
            printf("second writelock failure\n");
     }
        else {
            printf("second writelock sucess\n");
        }
    }
    pthread_rwlock_unlock(&rwlock);
    pthread_rwlock_unlock(&rwlock);
    return 0;
}
            

