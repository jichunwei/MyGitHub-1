#ifndef WIDGET_H
#define WIDGET_H

#include <QObject>
#include <QWidget>
#include <QtGui/QPushButton>
#include <QtGui/QHBoxLayout>
#include <QtGui/QVBoxLayout>

namespace Ui {
    class Widget;
}

class Widget : public QWidget
{
    Q_OBJECT

public:
    explicit Widget(QWidget *parent = 0);
    ~Widget();
/*
public slots:
  void deal_with_exit();
*/

private:
    Ui::Widget *ui;
};

#endif // WIDGET_H
