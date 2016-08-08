#include "ss.h"
/*
 SenderAndReceiver::SenderAndReceiver()
{
    QObject::connect(this,SIGNAL(mySignal()),
                     this,
                     SLOT(mySlot()));
    QObject::connect(this,SIGNAL(mySignal(double)),
                     this,
                     SLOT(mySlot(double)));

}

 SenderAndReceiver::~SenderAndReceiver()
{
    QObject::disconnect(this,SIGNAL(mySignal()),
                        this,
                        SLOT(mySlot()));
    QObject::disconnect(this,SIGNAL(mySignal(double)),
                        this,
                        SLOT(mySlot(double)));
}
*/

void SenderAndReceiver::senderSignal()
{
    emit   mySignal();
}

void SenderAndReceiver::senderSignal(double value)
{
    emit    mySignal(value);
}

void SenderAndReceiver::senderSignal(QString str)
{
    emit    mySignal(str);
}

void SenderAndReceiver::mySlot()
{
    qDebug()<<"receive without parameter";
    //std::cout<<"receive without parmeter"<<std::endl;
}

void SenderAndReceiver::mySlot(double value)
{
    qDebug()<<"value"<<value;
    //std::cout<<"value"<<value<<std::endl;
}

void SenderAndReceiver::mySlot(QString str)
{
    ;qDebug()<<"str"<<str;
    std::cout<<"str"<<str.toStdString()<<std::endl;
}
