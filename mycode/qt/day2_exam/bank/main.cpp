#include <QtGui/QApplication>
#include "widget.h"


int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    Widget w;

    QPushButton *commandButton1 =
                new QPushButton(&w);
    commandButton1->setText(QObject::trUtf8("查询余额"));
    commandButton1->setMinimumSize(1,2);
    QPushButton *commandButton2 =
                new QPushButton(&w);
    commandButton2->setText(QObject::trUtf8("存款"));
      commandButton1->setMinimumSize(1,2);
    QPushButton *commandButton3 =
                new QPushButton(&w);
    commandButton3->setText(QObject::trUtf8("取款"));
      commandButton1->setMinimumSize(1,2);
    QPushButton *commandButton4 =
                new QPushButton(&w);
    commandButton4->setText(QObject::trUtf8("转帐"));
      commandButton1->setMinimumSize(1,2);
    QPushButton *commandButton5 =
                new QPushButton(&w);
    commandButton5->setText(QObject::trUtf8("确认"));
      commandButton1->setMinimumSize(1,2);
    QPushButton *commandButton6 =
                new QPushButton(&w);
    commandButton6->setText(QObject::trUtf8("退出"));
      commandButton1->setMinimumSize(1,2);
    QVBoxLayout *buttonLayout =
             new QVBoxLayout();
 buttonLayout->addWidget(commandButton1);

 buttonLayout->addWidget(commandButton4);
 buttonLayout->addWidget(commandButton2);
 buttonLayout->setAlignment(Qt::AlignLeft);

 QVBoxLayout *buttonLayout1 =
          new QVBoxLayout();

 buttonLayout1->addWidget(commandButton5);
 buttonLayout1->addWidget(commandButton3);
 buttonLayout1->addWidget(commandButton6);
 buttonLayout1->setAlignment(Qt::AlignRight);

 QHBoxLayout *mainLayout =
            new QHBoxLayout();
    mainLayout->addLayout(buttonLayout);
    mainLayout->addLayout(buttonLayout1);

    w.setLayout(mainLayout);
    w.resize(300,150);
    w.show();

    return a.exec();
}
