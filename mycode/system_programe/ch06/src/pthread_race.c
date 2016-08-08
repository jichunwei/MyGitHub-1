#include <pthread.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

int flag;
typedef struct{
    char name[20];
    int time;
    int distance;
}RaceArg;

void * th_fn(void *arg)
{
    RaceArg* r = (RaceArg*)arg;
    if(r->distance <= 0)
        pthread_exit((void*)1);
    int i = 1;
    for(; i <= r->distance; i++)
    {
        if(flag==1)
        {
            pthread_exit((void*)1);
        }
        printf("%s(0x%lx) running %d\n",r->name,pthread_self(),i);
       //usleep(r->time);
        usleep((int)(drand48()*100));
    }
    flag=1;
    return (void*)0;
}

int main()
{
    int err;
    pthread_t rabbit,turtle;
    RaceArg  r_a,t_a;
    strcpy(r_a.name,"rabbit");
    r_a.distance = 100;
    r_a.time = (int)(drand48()*1000000);
    strcpy(t_a.name,"turtle");
    t_a.distance = 100;
    t_a.time = (int)(drand48()*1000000);
    printf("control thread id:0x%lx\n",pthread_self());
    flag=0;
    if((err = pthread_create(&rabbit,NULL,th_fn,(void*)&r_a)) != 0)
    {
        fprintf(stderr,"%s\n",strerror(err));
    }
    if((err = pthread_create(&turtle,NULL,th_fn,(void*)&t_a)) != 0)
    {
        fprintf(stderr,"%s\n",strerror(err));
    }
 //   sleep(10);
    int r;
    pthread_join(rabbit,(void*)&r);
    printf("rabbit res is %d\n",r);
    pthread_join(turtle,(void*)&r);
    printf("turtle res is %d\n",r);
    printf("race finished\n");
    return 0;
}

