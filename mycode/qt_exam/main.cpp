#include <QtGui/QApplication>
#include "widget.h"
#include <QtGui/QLabel>
#include <QtGui/QLineEdit>
#include <QtGui/QPushButton>
#include <QtGui/QGridLayout>
#include <QtGui/QVBoxLayout>
#include <QtGui/QHBoxLayout>
#include "mytext.h"
const int L=40;
const int W=30;



int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    Widget w;
    QLabel *nameLabel =
               new QLabel(&w);
    nameLabel->setText(QObject::trUtf8("calculator(c)"));
    QLabel *nameLabel1 =
               new QLabel(&w);
    nameLabel1->setText(QObject::trUtf8("editor(E)"));
    QLabel *nameLabel2 =
               new QLabel(&w);
    nameLabel2->setText(QObject::trUtf8("check(V)"));
    QLabel *nameLabel3 =
               new QLabel(&w);
    nameLabel3->setText(QObject::trUtf8("help(H)"));

    QHBoxLayout *nameLayout =
            new QHBoxLayout();
    nameLayout->addWidget(nameLabel);
    nameLayout->addWidget(nameLabel1);
    nameLayout->addWidget(nameLabel2);
    nameLayout->addWidget(nameLabel3);

   mytext *myEdit = new mytext(&w);
   myEdit->setText("");
   myEdit->setAlignment(Qt::AlignRight);
   myEdit->isReadOnly();
    QHBoxLayout *nameLayout1 =
            new QHBoxLayout();
    nameLayout1->addWidget(myEdit);

    QPushButton *num = new QPushButton[10];
    int index = 0;
    for(;index < 10;index++)
    {
        char buf[2];
        sprintf(buf,"%d",index);
        num[index].setText(buf);
        num[index].setMinimumSize(L,W);
    }
    QPushButton *backspace = new QPushButton(&w);
    backspace->setText("Bksp");
    backspace->setMinimumSize(L,W);
    QPushButton *ce = new QPushButton(&w);
    ce->setText("CE");
    ce->setMinimumSize(L,W);
    QPushButton *clr = new QPushButton(&w);
    clr->setText("clr");
    clr->setMinimumSize(L,W);
    QPushButton *convert = new QPushButton(&w);
    convert->setText("+/-");
    convert->setMinimumSize(L,W);
    QPushButton *div = new QPushButton(&w);
    div->setText("/");
    div->setMinimumSize(L,W);
    QPushButton *mul = new QPushButton(&w);
    mul->setText("*");
    mul->setMinimumSize(L,W);
    QPushButton *sub = new QPushButton(&w);
    sub->setText("-");
    sub->setMinimumSize(L,W);
    QPushButton *add = new QPushButton(&w);
    add->setText("+");
    add->setMinimumSize(L,W);
    QPushButton *equal = new QPushButton(&w);
    equal->setText("=");
    equal->setMinimumSize(L,W);
    QPushButton *point = new QPushButton(&w);
    point->setText(".");
    point->setMinimumSize(L,W);

    QGridLayout *gridlayout = new QGridLayout();
    gridlayout->addWidget(backspace,0,0);
    gridlayout->addWidget(ce,0,1);
    gridlayout->addWidget(clr,0,2);
    gridlayout->addWidget(convert,0,3);
    gridlayout->addWidget(&num[7],1,0);
    gridlayout->addWidget(&num[8],1,1);
    gridlayout->addWidget(&num[9],1,2);
    gridlayout->addWidget(div,1,3);
    gridlayout->addWidget(&num[4],2,0);
    gridlayout->addWidget(&num[5],2,1);
    gridlayout->addWidget(&num[6],2,2);
    gridlayout->addWidget(mul,2,3);
    gridlayout->addWidget(&num[1],3,0);
    gridlayout->addWidget(&num[2],3,1);
    gridlayout->addWidget(&num[3],3,2);
    gridlayout->addWidget(sub,3,3);
    gridlayout->addWidget(&num[0],4,0);
    gridlayout->addWidget(point,4,1);
    gridlayout->addWidget(equal,4,2);
    gridlayout->addWidget(add,4,3);

    QVBoxLayout mainLayout;
    mainLayout.addLayout(nameLayout);
    mainLayout.addLayout(nameLayout1);
    mainLayout.addLayout(gridlayout);
    w.setLayout(&mainLayout);
    w.resize(400,200);
    QObject::connect(&num[0],SIGNAL(clicked()),myEdit,SLOT(mySlot_0()));
    QObject::connect(&num[1],SIGNAL(clicked()),myEdit,SLOT(mySlot_1()));
    QObject::connect(&num[2],SIGNAL(clicked()),myEdit,SLOT(mySlot_2()));
    QObject::connect(&num[3],SIGNAL(clicked()),myEdit,SLOT(mySlot_3()));
    QObject::connect(&num[4],SIGNAL(clicked()),myEdit,SLOT(mySlot_4()));
    QObject::connect(&num[5],SIGNAL(clicked()),myEdit,SLOT(mySlot_5()));
    QObject::connect(&num[6],SIGNAL(clicked()),myEdit,SLOT(mySlot_6()));
    QObject::connect(&num[7],SIGNAL(clicked()),myEdit,SLOT(mySlot_7()));
    QObject::connect(&num[8],SIGNAL(clicked()),myEdit,SLOT(mySlot_8()));
    QObject::connect(&num[9],SIGNAL(clicked()),myEdit,SLOT(mySlot_9()));
    QObject::connect(backspace,SIGNAL(clicked()),myEdit,SLOT(mySlot_back()));
    QObject::connect(ce,SIGNAL(clicked()),myEdit,SLOT(mySlot_ce()));
    QObject::connect(convert,SIGNAL(clicked()),myEdit,SLOT(mySlot_convert()));
    QObject::connect(clr,SIGNAL(clicked()),myEdit,SLOT(mySlot_clr()));
    QObject::connect(div,SIGNAL(clicked()),myEdit,SLOT(mySlot_div()));
    QObject::connect(mul,SIGNAL(clicked()),myEdit,SLOT(mySlot_mul()));
    QObject::connect(add,SIGNAL(clicked()),myEdit,SLOT(mySlot_add()));
    QObject::connect(sub,SIGNAL(clicked()),myEdit,SLOT(mySlot_sub()));
    QObject::connect(point,SIGNAL(clicked()),myEdit,SLOT(mySlot_point()));
    QObject::connect(equal,SIGNAL(clicked()),myEdit,SLOT(mySlot_equal()));


    w.show();

    return a.exec();
}
