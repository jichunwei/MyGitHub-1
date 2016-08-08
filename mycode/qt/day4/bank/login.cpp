#include "login.h"
#include "widget.h"


Dialog::Dialog(QWidget *parent) :
    QDialog(parent)
{
   label_name = new QLabel(this);
   label_name->setText(QObject::trUtf8("账号"));
   passwd_label = new QLabel(this);
   passwd_lable->setTex(QObject::trUtf8("密码"));
   name_lineEdit = new QLineEdit(this);
   passwd_lineEdit = new QLineEdit(this);
   comit_button = new QPushButton(this);
   comit_button->setText(QObject::trUtf8("登录"));
   concel_button = new QPushButton(this);
   concel_button->setText(QObject::trUtf8("取消"));
   passwd_lineEdit->setEchoMode(QLineEdit::Password);
   ui->lineEdit_2->setEchoMode(QLineEdit::Password);
   QObject::connect(comit_button,
                     SIGNAL(clicked()),
                     this,
                     SLOT(dealWithLogin()));
   QObject::connect(cancel_button,
                    SIGNAL(clicked()),
                    this,
                    SLOT(close()));
   hBoxLayout1 = new QHBoxLayout();
   hBoxLayout2 = new QHBoxLayout();
   hBoxLayout3 = new QHBoxLayout();
   vBoxLayout = new QVBoxLayout();

   hBoxLayout1->addWidget(lable_name);
   hBoxLayout1->addWidget(name_lineEdit);
   hBoxLayout2->addWidget(passwd_lable);
   hBoxLayout2->addWidget(passwd_lineEdit);
   hBoxLayout3->addWidget(commit_button);
   hBoxLayout3->addWidget(concel_button);
   vBoxLayout->addLayout(hBoxLayout1);
   vBoxLayout->addLayout(hBoxLayout2);
   vBoxLayout->addLayout(hBoxLayout3);
   this->setLayout(vBoxLayout);
   this->resize(200,150);
}

Dialog::~Dialog()
{
    //delete ui;
}

void Dialog::dealWithLogin()
{
    QString userName = name_lineEdit->text();
    QString passwd = passwd_lineEdit->text();
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
       name_lineEdit->clear();
       passwd_lineEdit->clear();
       name_lineEdit->setFocus();
    }
}
