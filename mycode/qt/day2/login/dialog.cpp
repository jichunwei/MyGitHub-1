#include "dialog.h"
#include "ui_dialog.h"
#include <QObject>

Dialog::Dialog(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::Dialog)
{
    ui->setupUi(this);
    ui->lineEdit_2->setEchoMode(QLineEdit::Password);
    QObject::connect(ui->pushButton_2,
                     SIGNAL(clicked()),
                     this,
                     SLOT(dealWithLogin()));
}

Dialog::~Dialog()
{
    delete ui;
}

void Dialog::dealWithLogin(){
    QString userName = ui->lineEdit->text();
    QString passwd = ui->lineEdit_2->text();
    //以下是模拟查询数据的过程
    if(userName == "tan" && passwd == "tan"){
        this->accept();
        //显示用户登录的主界面
        //...
    }else{
        QMessageBox::warning(this,
                            QObject::trUtf8("警告"),
                            QObject::trUtf8("用户名或密码错误"),
                            QMessageBox::Yes | QMessageBox::No,
                            QMessageBox::Yes);
        ui->lineEdit->clear();
        ui->lineEdit_2->clear();
        ui->lineEdit->setFocus();;
    }

}
