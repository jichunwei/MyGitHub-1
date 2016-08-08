#ifndef MYTEXT_H
#define MYTEXT_H
#include <QtGui/QLineEdit>
#include <memory.h>
#include <cstdlib>
class mytext : public QLineEdit
{
    Q_OBJECT
 private:
     char *equation;
     int  len;
     float result;
public:
     mytext(QWidget *w):QLineEdit(w){
         this->len=0;      


         this->equation =new char[1024];
         memset(equation,0,1024*sizeof(char));

         this->result=0.0;
     }
 public slots:
     void operation();
     void mySlot_0();
     void mySlot_1();
     void mySlot_2();
     void mySlot_3();
     void mySlot_4();
     void mySlot_5();
     void mySlot_6();
     void mySlot_7();
     void mySlot_8();
     void mySlot_9();
     void mySlot_back();
     void mySlot_ce();
     void mySlot_clr();
     void mySlot_convert();
     void mySlot_div();
     void mySlot_equal();
     void mySlot_mul();
     void mySlot_add();
     void mySlot_sub();
     void mySlot_point();
};


#endif // MYTEXT_H
