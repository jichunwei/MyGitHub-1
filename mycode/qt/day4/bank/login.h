#ifndef LOGIN_H
#define LOGIN_H

#include <QMessageBox>
#include <QDialog>
#include <QtGui/QLineEdit>
#include <QtGui/QLabel>
#include <QtGui/QPushButton>
#include <QtGui/QHBoxLayout>
#include <QtGui/QVBoxLayout>


namespace Ui {
    class Dialog;
}

class Dialog : public QDialog
{
    Q_OBJECT

public:
    explicit Dialog(QWidget *parent = 0);
    ~Dialog();

public slots:
    void dealWithLogin();

private:
    QLabel *label_name;
    QLabel *passwd_label;
    QLineEdit *name_lineEdit;
    QLineEdit *passwd_lineEdit;
    QPushButton *comit_button;
    QPushButton *cancel_button;
    QHBoxLayout  *hBoxLayout1;
    QHBoxLayout  *hBoxLayout2;
    QHBoxLayout  *hBoxLayout3;
    QVBoxLayout  *vBoxLayout;

#endif // LOGIN_H
