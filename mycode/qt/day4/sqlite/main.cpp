#include <QtCore/QCoreApplication>
#include <QtSql/QSqlDatabase>
#include <QDebug>
#include <QtSql/QSqlQuery>

QSqlDatabase database;
QSqlQuery sqlQuery;


  bool openDatabase(){
    QSqlDatabase database = QSqlDatabase::addDatabase("QSQLITE");
        database.setDatabaseName("my_test.db");
        if(database.open()){
            qDebug()<<"open database success";
           // return true;
        }else{
            qDebug()<<"open database failure";
           // return false;
        }

        QString insertSql = "insert into student values(1,'xh','xh','shanghi')";
        sqlQuery.prepare(insertSql);
        sqlQuery.bindValue(0,2);
        sqlQuery.bindValue(1,'briup');
        sqlQuery.bindValue(1,"briup");
        sqlQuery.bindValue(3,"shanghai");

       bool result1 = Query.exec(insertSql);
        if(result1){
            qDebug()<<"insert success";
        }else {
          qDebug()<<"inset failure";
      }


        QSqlQuery   sqlQuery;
        QString sql ( "select *from student");
        bool result = sqlQuery.exec(sql);
        if(result)
        {
              int   id;
              QString name,passwd,address;
              while(sqlQuery.next()){
                  id = sqlQuery.value(0).toInt();
                  name = sqlQuery.value(1).toString();
                  passwd = sqlQuery.value(2).toString();
                  address = sqlQuery.value(3).toString();
                  qDebug()<<"id="<<id<<"name="<<name<<
                          "passwd="<<passwd<<"address="<<address;
              }
        }
        QSqlQuery deleteSql;
        QString deleteSql = "delete from student where id = 1";
        bool result2 = Query.exec(insertSql);
         if(result2){
             qDebug()<<"delete success";
         }else {
           qDebug()<<"delete failure";
       }

       //database.close();
    }

void closeDatabase(){
    database.close();
}

/*
static bool insertData(){
    QString insertSql = "insert into student values(?,?,?,?)";
    sqlQuery.prepare(insertSql);
    sqlQuery.bindValue(0,2);
    sqlQuery.bindValue(1,"briup");
    sqlQuery.bindValue(1,"briup");
    sqlQuery.bindValue(3,"shanghai");
    bool result = sqlQuery.exec(insertSql);
    if(result){
        qDebug()<<"insert success";
        return true;
    }else {
        qDebug()<<"inset failue";
        return false;
    }
}
*/
int main(int argc, char *argv[])
{
   /*在项目中如果要使用sql语句，必须手动在.pro文件中加上QT+=sql*/
    QCoreApplication a(argc, argv);
    openDatabase();
    closeDatabase();

    return a.exec();
}
