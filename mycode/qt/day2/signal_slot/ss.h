#ifndef SS_H
#define SS_H
//#include <QApplication>
#include <QObject>
#include <QDebug>
#include <iostream>
#include <QString>

class SenderAndReceiver : public QObject
{
    /*在QT中，如果在自己的类中要使用信号跟槽的机制，
    必须在类的开头使用Q_OBJECT宏的声明，并且Q_OBJECT是私有的，
◆moc 读 C++ 源文件,如果发现有 Q_OBJECT 宏声明的类,它就会生成另
外一个 C++ 源文件,这个新生成的文件中包含有该类的元对象代码。元对
象代码是 signal/slot 机制所必须的。
*/

    Q_OBJECT

/*
public:
    SenderAndReceiver();
    ~SenderAndReceiver();
*/
signals:
    void mySignal();
    void mySignal(double);
    void mySignal(QString);

public slots:
    void mySlot();
    void mySlot(double);
    void mySlot(QString);
public:
    void senderSignal();
    void senderSignal(double);
    void senderSignal(QString);
};

#endif // SS_H
