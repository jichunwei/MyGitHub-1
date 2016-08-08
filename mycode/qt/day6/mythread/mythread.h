#ifndef MYTHREAD_H
#define MYTHREAD_H

#include <QDebug>
#include  <QThread>
#include <QMutex>

static int global  = 0;
static QMutex mutex;

class MyThread : public QThread{
        Q_OBJECT
protected:
    void run();
};



#endif // MYTHREAD_H
