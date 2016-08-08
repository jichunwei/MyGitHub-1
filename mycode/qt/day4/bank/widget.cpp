#include "widget.h"
#include "ui_widget.h"
#include  <QObject>


Widget::Widget(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::Widget)
{
    ui->setupUi(this);
    this->setWindowTitle("ATM");

    QObject::connect(ui->pushButton,
                     SIGNAL(clicked()),
                     this,
                     SLOT(serach()));
    QObject::connect(ui->pushButton_2,
                     SIGNAL(clicked()),
                     this,
                     SLOT(withdraw(double)));
    QObject::connect(ui->pushButton_3,
                     SIGNAL(clicked()),
                     this,
                     SLOT(depoist(double)));
    QObject::connect(ui->pushButton_4,
                     SIGNAL(clicked()),
                     this,
                     SLOT(transfer(long,double)));
    QObject::connect(ui->pushButton_5,
                     SIGNAL(clicked()),
                     this,
                     SLOT(quit()));

}


void Widget::serach(){

}

void Widget::withdraw(double value){
    emit withdraw(value);
}

void Widget::depoist(double value){
    emit depoist(value);
}

void Widget::transfer(long account_id,double value){
    emit transfer(account_id,value);
}

void Widget::quit(){

}

Widget::~Widget()
{
    delete ui;
}
