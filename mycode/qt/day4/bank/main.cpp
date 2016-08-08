#include <QtGui/QApplication>
#include "widget.h"
#include "login.h"

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    //Widget w;
    //w.show();

    Dialog dialog;
    dialog.show();
    return a.exec();
}
