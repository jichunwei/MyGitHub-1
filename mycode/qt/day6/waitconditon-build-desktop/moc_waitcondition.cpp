/****************************************************************************
** Meta object code from reading C++ file 'waitcondition.h'
**
** Created: Sat Oct 29 11:14:09 2011
**      by: The Qt Meta Object Compiler version 62 (Qt 4.7.0)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../waitconditon/waitcondition.h"
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'waitcondition.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 62
#error "This file was generated using the moc from 4.7.0. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
static const uint qt_meta_data_Wait[] = {

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

static const char qt_meta_stringdata_Wait[] = {
    "Wait\0"
};

const QMetaObject Wait::staticMetaObject = {
    { &QThread::staticMetaObject, qt_meta_stringdata_Wait,
      qt_meta_data_Wait, 0 }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &Wait::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *Wait::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *Wait::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_Wait))
        return static_cast<void*>(const_cast< Wait*>(this));
    return QThread::qt_metacast(_clname);
}

int Wait::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QThread::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    return _id;
}
static const uint qt_meta_data_Wakeup[] = {

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

static const char qt_meta_stringdata_Wakeup[] = {
    "Wakeup\0"
};

const QMetaObject Wakeup::staticMetaObject = {
    { &QThread::staticMetaObject, qt_meta_stringdata_Wakeup,
      qt_meta_data_Wakeup, 0 }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &Wakeup::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *Wakeup::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *Wakeup::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_Wakeup))
        return static_cast<void*>(const_cast< Wakeup*>(this));
    return QThread::qt_metacast(_clname);
}

int Wakeup::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QThread::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    return _id;
}
QT_END_MOC_NAMESPACE
