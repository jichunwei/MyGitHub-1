#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct{
    int i;
    pthread_cond_t rc;
    pthread_mutex_t rm;
    int r_counter;
    pthread_cond_t wc;
    pthread_mutex_t wm;
    int w_counter;
}Storage;

void set_data(Storage *s,int i)
{
    s->i = i;
}

int get_data(Storage *s)
{
    return s->i;
}

void *set_th(void *arg)
{
    Storage *s = (Storage *)arg;
    int i = 1;
    for(; i <= 100; i++)
    {
        set_data(s,i+100);
//        printf("0x%1x(%-3d):'put'\n",pthread_self(),i);
        pthread_mutex_lock(&s->rm);
        while(s->r_counter < 2)
        {
            pthread_mutex_unlock(&s->rm);
            usleep(100);
            pthread_mutex_lock(&s->rm);
        }
        s->r_counter = 0;
        pthread_mutex_unlock(&s->rm);
        pthread_cond_broadcast(&s->rc);
        pthread_mutex_lock(&s->wm);
        s->w_counter = 1;
        pthread_cond_wait(&s->wc,&s->wm);
      //  s->w_counter = 0;
        pthread_mutex_unlock(&s->wm);
    }
    return (void*)0;
}

void *get_th(void *arg)
{
    Storage *s = (Storage *)arg;
    int i = 1, d;
    for(; i <= 100; i++)
    {
        pthread_mutex_lock(&s->rm);
        s->r_counter++;
        pthread_cond_wait(&s->rc,&s->rm);
//        s->r_counter--;
        pthread_mutex_unlock(&s->rm);
        d = get_data(s);
        printf("0x%1x(%-3d):%5d\n",pthread_self(),i,d);

        pthread_mutex_lock(&s->wm);
        while(s->w_counter != 1)
        {
            pthread_mutex_unlock(&s->wm);
            usleep(100);
            pthread_mutex_lock(&s->wm);
        }
        pthread_mutex_unlock(&s->wm);
        pthread_cond_broadcast(&s->wc);
      //  printf("0x%1x(%-3d):%5d\n",pthread_self(),i,d);
    }
    return (void*)0;
}

int main()
{
    int err;
    pthread_t wth,rth1,rth2;
    Storage s;
    s.r_counter = 0;
    s.w_counter = 0;
    pthread_mutex_init (&s.rm,NULL);
    pthread_mutex_init (&s.wm,NULL);
    pthread_cond_init(&s.rc,NULL);
    pthread_cond_init(&s.wc,NULL);
    if((err = pthread_create(&rth1,NULL,get_th,(void*)&s)) != 0){
        fprintf(stderr,"%s\n",strerror(err));
    }
    if((err = pthread_create(&rth2,NULL,get_th,(void*)&s)) != 0){
        fprintf(stderr,"%s\n",strerror(err));
    }
    if((err = pthread_create(&wth,NULL,set_th,(void*)&s)) != 0){
        fprintf(stderr,"%s\n",strerror(err));
    }
    pthread_join(rth1,NULL);
    pthread_join(rth2,NULL);
    pthread_join(wth,NULL);
    return 0;
}


