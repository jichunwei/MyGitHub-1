#include <QtCore/QCoreApplication>
#include "mythread.h"

/*在qt应用程序中：
要用thread线程时要在.pro文件中加入CONFIG ＋＝ thread;*/
int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv);
    /*在线程对象的调用start方法，表示线程的开启，
      而实际去执行是线程类中重写的run()函数*/
    MyThread *myThread = new MyThread();
   // myThread->start();


    int i,j,k;
    MyThread *threadArray[10];
    for(i = 0; i < 10; i++){
        threadArray[i] = new MyThread();
    }
    for(j = 0; j < 10; j++){
        threadArray[j]->start();
    }
    qDebug()<<"main thread is running..";
    //主线程等待子线程结束

    for(k = 0; k < 10; k++){
        threadArray[k]->wait();
    }
    qDebug()<<"main thread is finsh..";
    return a.exec();
}
