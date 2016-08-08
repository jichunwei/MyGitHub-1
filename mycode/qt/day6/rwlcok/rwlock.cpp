#include "rwlock.h"

void Reader::run(){
    readwrite_lock.lockForRead();
    qDebug()<<Reader::currentThreadId()<<"reader global:"<<global;
    Reader::sleep(2);
    readwrite_lock.unlock();
}

void Writer::run(){
    global += 5;
    qDebug()<<Writer::currentThreadId()<<"writer global:"<<global;
    Writer::sleep(2);
    readwrite_lock.unlock();
}
