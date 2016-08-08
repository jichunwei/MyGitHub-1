#include "mainwindow.h"
#include "ui_mainwindow.h"

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    QLabel *nameLabel =
                   new QLabel(this);
        nameLabel->setText(QObject::trUtf8("计算器(c)"));
        QLabel *nameLabel1 =
                   new QLabel(this);
        nameLabel1->setText(QObject::trUtf8("编辑(E)"));
        QLabel *nameLabel2 =
                   new QLabel(this);
        nameLabel2->setText(QObject::trUtf8("查看(V)"));
        QLabel *nameLabel3 =
                   new QLabel(this);
        nameLabel3->setText(QObject::trUtf8("帮助(H)"));

        QHBoxLayout *nameLayout =
                new QHBoxLayout();
        nameLayout->addWidget(nameLabel);
        nameLayout->addWidget(nameLabel1);
        nameLayout->addWidget(nameLabel2);
        nameLayout->addWidget(nameLabel3);

        QLineEdit *nameEdit = new QLineEdit(this);
        nameEdit->setText("");
        nameEdit->setAlignment (Qt::AlignRight);
        QHBoxLayout *nameLayout1 =
                new QHBoxLayout();
        nameLayout1->addWidget(nameEdit);

        QPushButton *commandButton1 =
                    new QPushButton(this);
        commandButton1->setText(QObject::trUtf8("Bksp"));
        QPushButton *commandButton2 =
                    new QPushButton(this);
        commandButton2->setText(QObject::trUtf8("CE"));
        QPushButton *commandButton3 =
                    new QPushButton(this);
        commandButton3->setText(QObject::trUtf8("Clr"));
        QPushButton *commandButton4 =
                    new QPushButton(this);
        commandButton4->setText(QObject::trUtf8("+/-"));
        QPushButton *commandButton5 =
                    new QPushButton(this);
        commandButton5->setText(QObject::trUtf8("7"));
        QPushButton *commandButton6 =
                    new QPushButton(this);
        commandButton6->setText(QObject::trUtf8("8"));
        QPushButton *commandButton7 =
                    new QPushButton(this);
        commandButton7->setText(QObject::trUtf8("9"));
        QPushButton *commandButton8 =
                    new QPushButton(this);
        commandButton8->setText(QObject::trUtf8("/"));
        QPushButton *commandButton9 =
                    new QPushButton(this);
        commandButton9->setText(QObject::trUtf8("4"));
        QPushButton *commandButton10 =
                    new QPushButton(this);
        commandButton10->setText(QObject::trUtf8("5"));
        QPushButton *commandButton11 =
                    new QPushButton(this);
        commandButton11->setText(QObject::trUtf8("6"));
        QPushButton *commandButton12 =
                    new QPushButton(this);
        commandButton12->setText(QObject::trUtf8("*"));
        QPushButton *commandButton13 =
                    new QPushButton(this);
        commandButton13->setText(QObject::trUtf8("1"));
        QPushButton *commandButton14 =
                    new QPushButton(this);
        commandButton14->setText(QObject::trUtf8("2"));
        QPushButton *commandButton15 =
                    new QPushButton(this);
        commandButton15->setText(QObject::trUtf8("3"));
        QPushButton *commandButton16 =
                    new QPushButton(this);
        commandButton16->setText(QObject::trUtf8("-"));
        QPushButton *commandButton17 =
                    new QPushButton(this);
        commandButton17->setText(QObject::trUtf8("0"));
        QPushButton *commandButton18 =
                    new QPushButton(this);
        commandButton18->setText(QObject::trUtf8("."));
        QPushButton *commandButton19 =
                    new QPushButton(this);
        commandButton19->setText(QObject::trUtf8("="));
        QPushButton *commandButton20 =
                    new QPushButton(this);
        commandButton20->setText(QObject::trUtf8("+"));

        QGridLayout *gridlayout = new QGridLayout();
        gridlayout->addWidget(commandButton1,0,0);
        gridlayout->addWidget(commandButton2,0,1);
        gridlayout->addWidget(commandButton3,0,2);
        gridlayout->addWidget(commandButton4,0,3);
        gridlayout->addWidget(commandButton5,1,0);
        gridlayout->addWidget(commandButton6,1,1);
        gridlayout->addWidget(commandButton7,1,2);
        gridlayout->addWidget(commandButton8,1,3);
        gridlayout->addWidget(commandButton9,2,0);
        gridlayout->addWidget(commandButton10,2,1);
        gridlayout->addWidget(commandButton11,2,2);
        gridlayout->addWidget(commandButton12,2,3);
        gridlayout->addWidget(commandButton13,3,0);
        gridlayout->addWidget(commandButton14,3,1);
        gridlayout->addWidget(commandButton15,3,2);
        gridlayout->addWidget(commandButton16,3,3);
        gridlayout->addWidget(commandButton17,4,0);
        gridlayout->addWidget(commandButton18,4,1);
        gridlayout->addWidget(commandButton19,4,2);
        gridlayout->addWidget(commandButton20,4,3);
}

MainWindow::~MainWindow()
{
    delete ui;
}
