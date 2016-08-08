#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

long long int mul(int i)
{
    if(i==1) return 1;
    return i*mul(i-1);
}
void  *th_cal(void *arg)
{
    int i = (int)arg;
    long long int *r = (long long *)malloc(sizeof(long long int));
     *r = mul(i);
    printf("0x%lx: %lld\n",pthread_self(),*r);
    return (void*)r;
}

int main(int argc,char *argv[])
{
    int err;
    int k=atoi(argv[1]);
    pthread_t th1;
    if((err = pthread_create(&th1,NULL,th_cal,(void*)k)) != 0)
    {
        fprintf(stderr,"%s\n",strerror(err));
    }
    long long int *res;
    pthread_join(th1 ,(void*)&res);
    printf("0x%lx: %lld\n",pthread_self(),*res);
    free(res);
    return 0;
}
    


    


