#ifndef SEMAPHORE_H
#define SEMAPHORE_H

#include <QThread>
#include <qdebug.h>
#include <qsemaphore.h>

static int  global = 3;
static QSemaphore semaphore(3);

class Producter : public QThread{
    Q_OBJECT
protected:
    void run();
};

class Consumer : public QThread{
    Q_OBJECT
protected:
    void run();
};

#endif // SEMAPHORE_H
