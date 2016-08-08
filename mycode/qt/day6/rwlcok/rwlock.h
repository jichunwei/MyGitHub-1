#ifndef RWLOCK_H
#define RWLOCK_H

#include <QThread>
#include <qdebug.h>
#include <qreadwritelock.h>

static int global = 0;
static QReadWriteLock readwrite_lock;

class Reader : public QThread{
    Q_OBJECT
protected:
    void run();
};

class Writer : public QThread{
    Q_OBJECT
protected:
    void run();
};

#endif // RWLOCK_H
