#include <QtGui/QApplication>
#include "widget.h"
#include <QtGui/QTextEdit>
#include <QtGui/QStackedLayout>
#include <QtGui/QComboBox>
#include <QtGui/QVBoxLayout>
int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    Widget w;
    QWidget *first = new QWidget(&w);
    QWidget *second = new QWidget(&w);
    QWidget *thrid = new QWidget(&w);
    QTextEdit *firstEdit =
            new QTextEdit(first);
    QTextEdit *secondEdit =
            new QTextEdit(second);
    QTextEdit *thridEdit =
            new QTextEdit(thrid);
    firstEdit->setText("first page..");
    secondEdit->setText("second page..");
    thridEdit->setText("thrid page..");


    QStackedLayout *stackLayout =
            new QStackedLayout();
    stackLayout->addWidget(first);
    stackLayout->addWidget(second);
    stackLayout->addWidget(thrid);
    QComboBox *comboBox =
            new QComboBox();
    comboBox->addItem(QObject::trUtf8("第一页"));
    comboBox->addItem(QObject::trUtf8("第二页"));
    comboBox->addItem(QObject::trUtf8("第三页"));

    QObject::connect(comboBox,SIGNAL(currentIndexChanged(int)),
                     stackLayout,
                     SLOT(setCurrentIndex(int)));

    QVBoxLayout *vboxLayout =
            new QVBoxLayout();
    vboxLayout->addWidget(comboBox);
    vboxLayout->addLayout(stackLayout);
    w.setLayout(vboxLayout);
    w.resize(300,200);
    w.show();


    return a.exec();
}
