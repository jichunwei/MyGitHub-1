#include "account.h"
#include <malloc.h>
#include <assert.h>
#include <stdio.h>
//创建帐户
Account * create_account(int code,double balance)
{
    Account *a = (Account*)malloc(sizeof(Account));
    assert(a != NULL);
    a->code = code;
    a->balance = balance;
//    pthread_mutex_init(&a->mutex,NULL);
    pthread_rwlock_init(&a->rwlock,NULL);
    return a;
}
//销毁账户
void destroy_account(Account *a)
{
    assert(a != NULL);
   // pthread_mutex_destroy(&a->mutex);
    pthread_rwlock_destroy(&a->rwlock);
    free(a);
}
//从账户a中取出amt的钱
double withdraw(Account *a,double amt)
{
    assert(a != NULL);
//    pthread_mutex_lock(&a->mutex);
    pthread_rwlock_wrlock(&a->rwlock);
    printf("write lock success\n");
    if(amt < 0 || amt > a->balance)
    {
      //  pthread_mutex_unlock(&a->mutex);
        pthread_rwlock_unlock(&a->rwlock);
        return 0.0;
    }
    double t = a->balance;
    sleep(1);
    t -= amt;
    a->balance =t ;
  //  pthread_mutex_unlock(&a->mutex);
    pthread_rwlock_unlock(&a->rwlock);
    return amt;
}
//向账户a中存入amt的钱
double deposit(Account *a,double amt)
{
    assert(a != NULL);
   // pthread_mutex_lock(&a->mutex);
    pthread_rwlock_wrlock(&a->rwlock);
    printf("write lock success\n");
    if(amt < 0)
    {
       // pthread_mutex_unlock(&a->mutex);
        pthread_rwlock_unlock(&a->rwlock);
        return 0.0;
    }
    double t = a->balance;
    sleep(1);
    t += amt;
    a->balance =t ;
   // pthread_mutex_unlock(&a->mutex);
        pthread_rwlock_unlock(&a->rwlock);
    return amt;
}

//查询账户a的余额
double get_balance(Account *a)
{
    assert(a != NULL);
    pthread_rwlock_rdlock(&a->rwlock);
    printf("read lock success\n");
    double t = a->balance;
    sleep(1);
    pthread_rwlock_unlock(&a->rwlock);
    return t;
}



