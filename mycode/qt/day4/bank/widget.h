#ifndef WIDGET_H
#define WIDGET_H

#include <QWidget>
#include <QObject>
#include <QtGui/QPushButton>

namespace Ui {
    class Widget;
}

class Widget : public QWidget
{
    Q_OBJECT

public:
    explicit Widget(QWidget *parent = 0);
    ~Widget();


public slots:
    void serach();
    void withdraw(double);
    void depoist(double);
    void transfer(long,double);
    void quit();

private:
    Ui::Widget *ui;

};

#endif // WIDGET_H
