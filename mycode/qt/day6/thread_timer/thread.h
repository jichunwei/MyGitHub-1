#ifndef THREAD_H
#define THREAD_H
#include <qdebug.h>
#include <qthread.h>
#include <QObject>

class Timer : public QThread{
    Q_OBJECT
protected:
    void run();
signals:
    void currentTime(QString);

};


#endif // THREAD_H
