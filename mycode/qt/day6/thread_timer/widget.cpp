#include "widget.h"
#include "ui_widget.h"
#include "thread.h"

Widget::Widget(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::Widget)
{
    ui->setupUi(this);
    Timer *timer = new Timer();
    QObject::connect(timer,SIGNAL(currentTime(QString)),this,
                     SLOT(getCurrentTime(QString)));
    timer->start();
}

Widget::~Widget()
{
    delete ui;
}

void Widget::getCurrentTime(QString time){
    ui->label->setText(time);
}
