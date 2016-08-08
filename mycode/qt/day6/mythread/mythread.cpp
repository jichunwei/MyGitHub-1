#include "mythread.h"

void MyThread::run(){
    mutex.lock();
    global++;
   // qDebug()<<"my thread is running";
     MyThread::sleep(1);
    qDebug()<<MyThread::currentThreadId()<<"global:"<<global;
    mutex.unlock();

}
