#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

pthread_mutex_t  mutex;

int main(int argc ,char *argv[])
{
    if(argc < 2)
    {
        fprintf(stderr,"-usage:%s [error]|[normal]|[recreusive]\n",argv[0]);
        exit(1);
    }
    pthread_mutexattr_t  mutexattr;
    pthread_mutexattr_init(&mutexattr);
    if(!strcmp(argv[1],"error")){
        pthread_mutexattr_settype(&mutexattr,PTHREAD_MUTEX_ERRORCHECK);
    }else if(!strcmp(argv[1],"normal")){
        pthread_mutexattr_settype(&mutexattr,PTHREAD_MUTEX_NORMAL);
    }else if(!strcmp(argv[1],"recursive")){
        pthread_mutexattr_settype(&mutexattr,PTHREAD_MUTEX_RECURSIVE);
    }
    pthread_mutex_init(&mutex,&mutexattr);
 //   pthread_mutex_init(&mutex,NULL);
    if(pthread_mutex_lock(&mutex) != 0)
    {
        printf("lock failure\n");
    }
    else{
        printf("lock success\n");
    }
    if(pthread_mutex_lock(&mutex) != 0)
    {
        printf("lock failure\n");
    }
    else{
        printf("lock success\n");
    }
    pthread_mutex_unlock(&mutex);
    pthread_mutex_unlock(&mutex);
    exit(0);
}
        
        



        
            


    
