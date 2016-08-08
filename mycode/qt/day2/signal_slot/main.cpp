#include "ss.h"

int main(void)
{
    SenderAndReceiver  *ss1 = new SenderAndReceiver();
    SenderAndReceiver  *ss2 = new SenderAndReceiver();
    QObject::connect(ss1,SIGNAL(mySignal()),
                     ss2,
                     SLOT(mySlot()));
    QObject::connect(ss1,SIGNAL(mySignal(double)),
                     ss2,
                     SLOT(mySlot(double)));

    QObject::connect(ss1,SIGNAL(mySignal(QString)),
                     ss2,
                     SLOT(mySlot(QString)));

    ss1->senderSignal();
    double value = 20.2;
    ss1->senderSignal(value);
    QString str = "xh sb";
    ss1->senderSignal(str);

    return 0;

}
