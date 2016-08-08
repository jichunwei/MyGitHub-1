#ifndef WAITCONDITION_H
#define WAITCONDITION_H

#include <qthread.h>
#include <qmutex.h>
#include <qwaitcondition.h>
#include <qdebug.h>


static int global = 0;
static QMutex mutex;
static QWaitCondition waitcondition;

class Wait :  public QThread
{
       Q_OBJECT
protected:
    void run();

};

class Wakeup : public QThread{
    Q_OBJECT
protected:
    void run();

};

#endif // WAITCONDITION_H
