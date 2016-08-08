#include <qapplication.h>
#include <qwidget.h>
#include <qpushbutton.h>

int main(int argc,char *argv[])
{
	QApplication a(argc,argv);

	QWidget mainwindow;
	mainwindow.setMinimumSize(200,100);
	mainwindow.setMaximumSize(200,100);

	QPushButton helloworld("Hello World!",&mainwindow);
	helloworld.setGeometry(20,20,160,60);

	a.setActiveWindow(&mainwindow);
	mainwindow.show();

	return a.exec();
}
