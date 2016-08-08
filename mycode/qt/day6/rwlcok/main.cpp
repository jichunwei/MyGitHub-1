#include <QtCore/QCoreApplication>
#include "rwlock.h"

int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv);

    Reader *reader1 = new Reader();
    Reader *reader2 = new Reader();
    reader1->start();
    reader2->start();

    Writer *writer1 = new Writer();
    Writer *writer2 = new Writer();
    writer1->start();
    writer2->start();
    Reader *reader3 = new Reader();
    Reader *reader4 = new Reader();
    reader3->start();
    reader4->start();

    return a.exec();
}
