#include <QApplication>
#include <QLabel>
#include <QPushButton>

int main(int argc,char *argv[])
{
	//QApplication:表示一个qt的应用程序。
	QApplication app(argc,argv);
	QPushButton *button = new QPushButton("Quit");
	QObject::connect(button,SIGNAL(clicked()),&app,SLOT(quit()));
	button->show();
	return app.exec();
}
