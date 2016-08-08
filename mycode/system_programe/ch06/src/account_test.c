#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "account.h"

typedef struct{
    char name[20];
    Account *account;
    double amt;
}OperArg;

void* withdraw_fn(void *arg)
{
    OperArg* oa = (OperArg*)arg;
    double amt = withdraw(oa->account,oa->amt);
    printf("%s(0x%lx) withdraw %f from account %d\n",oa->name,pthread_self(),amt,oa->account->code);
    return (void*)0;
}


void *check_fn(void *arg)
{
    OperArg* oa = (OperArg*)arg;
    double amt = get_balance(oa->account);
    printf("%8s(0x%lx) check %f from account %d\n",oa->name,pthread_self(),amt,oa->account->code);
    return (void*)0;
}

int main()
{
    int err;
    pthread_t boy,girl;
    Account *a = create_account(100001,10000);
    OperArg o1,o2;
    strcpy(o1.name,"boy");
    o1.account =a;
    o1.amt = 10000;
    strcpy(o2.name,"girl");
    o2.account =a;
    o2.amt = 10000;
    if((err = pthread_create(&boy,NULL,check_fn,(void*)&o1)) != 0){
        fprintf(stderr,"%s\n",strerror(err));
    }
    if((err = pthread_create(&girl,NULL,check_fn,(void*)&o2)) != 0){
        fprintf(stderr,"%s\n",strerror(err));
    }
    pthread_join(boy, NULL);
    pthread_join(girl, NULL);
    printf("account balance :%1f\n",get_balance(a));
    exit(0);
}




                    
