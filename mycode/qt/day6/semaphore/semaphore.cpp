#include "semaphore.h"

void Producter::run(){
    while(1){
        if(semaphore.available() < 3){
            semaphore.release(1);
            global++;
            qDebug()<<"Producter availablle resource:"<<semaphore.available();
            Consumer::sleep(1);
        }else {
            qDebug()<<"producer sleep 1 second";
        }
    }
}

void Consumer::run(){
    while(1){
        if(semaphore.available() > 0){
            semaphore.acquire(1);
            global--;
            qDebug()<<"consumer availablle resource:"<<semaphore.available();
            Consumer::sleep(1);
        }else{
            qDebug()<<"consumer sleep one second";
            Consumer::sleep(1);
        }
    }
}
