#include "thread.h"

void Timer::run(){
    static int i = 0;
    QString str;
    for(;;){
        i++;
        Timer::sleep(1);
        emit currentTime(str.setNum(i));
    }
}
