#include <qapplication.h>
#include <qwidget.h>
#include <qpushbutton.h>
#include <qfront.h>
#include <qlayout.h>

class My_widget : public QWidget
{
	public:
		my_widget();
}

My_widet::My_widget()
{
	setMinimumSize(200,200);

	QPushButton *b1 = new QPushButton(this);
	b1->setMinmumSize(200,100);
	b1->setFont(QFont("Times",18,QFont::Bold));

	QPushButton *b2 = new QPushButton(this);
	b2->sertFont(QFont("Times",18,QFont::Bold));
}
