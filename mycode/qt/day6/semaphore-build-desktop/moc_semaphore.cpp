/****************************************************************************
** Meta object code from reading C++ file 'semaphore.h'
**
** Created: Sat Oct 29 14:09:23 2011
**      by: The Qt Meta Object Compiler version 62 (Qt 4.7.0)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../semaphore/semaphore.h"
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'semaphore.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 62
#error "This file was generated using the moc from 4.7.0. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
static const uint qt_meta_data_Producter[] = {

 // content:
       5,       // revision
       0,       // classname
       0,    0, // classinfo
       0,    0, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

       0        // eod
};

static const char qt_meta_stringdata_Producter[] = {
    "Producter\0"
};

const QMetaObject Producter::staticMetaObject = {
    { &QThread::staticMetaObject, qt_meta_stringdata_Producter,
      qt_meta_data_Producter, 0 }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &Producter::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *Producter::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *Producter::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_Producter))
        return static_cast<void*>(const_cast< Producter*>(this));
    return QThread::qt_metacast(_clname);
}

int Producter::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QThread::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    return _id;
}
static const uint qt_meta_data_Consumer[] = {

 // content:
       5,       // revision
       0,       // classname
       0,    0, // classinfo
       0,    0, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

       0        // eod
};

static const char qt_meta_stringdata_Consumer[] = {
    "Consumer\0"
};

const QMetaObject Consumer::staticMetaObject = {
    { &QThread::staticMetaObject, qt_meta_stringdata_Consumer,
      qt_meta_data_Consumer, 0 }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &Consumer::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *Consumer::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *Consumer::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_Consumer))
        return static_cast<void*>(const_cast< Consumer*>(this));
    return QThread::qt_metacast(_clname);
}

int Consumer::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QThread::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    return _id;
}
QT_END_MOC_NAMESPACE
