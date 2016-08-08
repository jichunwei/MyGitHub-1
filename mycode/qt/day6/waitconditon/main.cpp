#include <QtCore/QCoreApplication>
#include "waitcondition.h"

int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv);
    Wait *wait1 = new Wait();
    wait1->start();
    Wait *wait2 = new Wait();
    wait2->start();

    Wakeup *wakeup1 = new Wakeup();
    wakeup1->start();
    sleep(2);
    Wakeup *wakeup2 = new Wakeup();
    wakeup2->start();

    return a.exec();
}
