#include <qapplication.h>
#include <qpushbutton.h>
#include <qfont.h>
#include <QVBoxLayout>

int main(int argc,char *argv[])
{
	QApplication a(argc,argv);
	QVBoxLayout	box;
	QPushButton quit("Quit");
	quit.setFont(QFont("times",18,QFont::Bold));

	QObject::connect(&quit,SIGNAL(clicked()),&a,SLOT(quit()));

//	a.setMainWidget(&box);
//	box.show();

	return a.exec();
}
