#include "waitcondition.h"

void Wait::run(){
    qDebug()<<Wait::currentThreadId();
    waitcondition.wait(&mutex);
    qDebug()<<Wait::currentThreadId()<<"global:"<<global;
    Wait::sleep(2);

}

void Wakeup::run(){
    mutex.lock();
    global = global + 5;
    Wakeup::sleep(2);
    mutex.unlock();
   // waitcondition.wakeAll();
    waitcondition.wakeOne();
}
