#include <QtCore/QCoreApplication>
#include "semaphore.h"

int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv);

    Consumer *consumer = new Consumer();
    consumer->start();
    sleep(1);

    Producter *producter  = new Producter();
    producter->start();

    return a.exec();
}
