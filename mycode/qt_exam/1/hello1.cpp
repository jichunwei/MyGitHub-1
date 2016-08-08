#include <qapplication.h>
#include <qpushbutton.h>
#include <QObject>

int main( int argc, char **argv )
{
	QApplication a( argc, argv );
//	QPushButton hello( "Hello world!", 0 );
	QPushButton *hello = new QPushButton(QObject::trUtf8("宋江"));
	hello->resize( 200, 100 );
	hello->show();

	return a.exec();
}

