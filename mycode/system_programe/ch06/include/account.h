#ifndef __ACCOUNT_H__
#define __ACCOUNT_H__
#include <pthread.h>
typedef struct{
    int code;
    double balance;
//    pthread_mutex_t mutex;
    pthread_rwlock_t  rwlock;
}Account;

//创建帐户
extern Account * create_account(int code,double balance);
//销毁账户
extern void destroy_account(Account *a);
//从账户a中取出amt的钱
extern double withdraw(Account *a,double amt);
//向账户a中存入amt的钱
extern double deposit(Account *a,double amt);
//查询账户a的余额
extern double get_balance(Account *a);
#endif


