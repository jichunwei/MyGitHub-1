/****************************************************************************
** Meta object code from reading C++ file 'rwlock.h'
**
** Created: Sat Oct 29 10:44:28 2011
**      by: The Qt Meta Object Compiler version 62 (Qt 4.7.0)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../rwlcok/rwlock.h"
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'rwlock.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 62
#error "This file was generated using the moc from 4.7.0. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
static const uint qt_meta_data_Reader[] = {

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

static const char qt_meta_stringdata_Reader[] = {
    "Reader\0"
};

const QMetaObject Reader::staticMetaObject = {
    { &QThread::staticMetaObject, qt_meta_stringdata_Reader,
      qt_meta_data_Reader, 0 }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &Reader::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *Reader::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *Reader::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_Reader))
        return static_cast<void*>(const_cast< Reader*>(this));
    return QThread::qt_metacast(_clname);
}

int Reader::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QThread::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    return _id;
}
static const uint qt_meta_data_Writer[] = {

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

static const char qt_meta_stringdata_Writer[] = {
    "Writer\0"
};

const QMetaObject Writer::staticMetaObject = {
    { &QThread::staticMetaObject, qt_meta_stringdata_Writer,
      qt_meta_data_Writer, 0 }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &Writer::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *Writer::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *Writer::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_Writer))
        return static_cast<void*>(const_cast< Writer*>(this));
    return QThread::qt_metacast(_clname);
}

int Writer::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QThread::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    return _id;
}
QT_END_MOC_NAMESPACE
