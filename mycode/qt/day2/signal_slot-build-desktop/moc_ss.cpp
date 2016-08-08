/****************************************************************************
** Meta object code from reading C++ file 'ss.h'
**
** Created: Tue Oct 25 11:21:17 2011
**      by: The Qt Meta Object Compiler version 62 (Qt 4.7.0)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../signal_slot/ss.h"
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'ss.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 62
#error "This file was generated using the moc from 4.7.0. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
static const uint qt_meta_data_SenderAndReceiver[] = {

 // content:
       5,       // revision
       0,       // classname
       0,    0, // classinfo
       6,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       3,       // signalCount

 // signals: signature, parameters, type, tag, flags
      19,   18,   18,   18, 0x05,
      30,   18,   18,   18, 0x05,
      47,   18,   18,   18, 0x05,

 // slots: signature, parameters, type, tag, flags
      65,   18,   18,   18, 0x0a,
      74,   18,   18,   18, 0x0a,
      89,   18,   18,   18, 0x0a,

       0        // eod
};

static const char qt_meta_stringdata_SenderAndReceiver[] = {
    "SenderAndReceiver\0\0mySignal()\0"
    "mySignal(double)\0mySignal(QString)\0"
    "mySlot()\0mySlot(double)\0mySlot(QString)\0"
};

const QMetaObject SenderAndReceiver::staticMetaObject = {
    { &QObject::staticMetaObject, qt_meta_stringdata_SenderAndReceiver,
      qt_meta_data_SenderAndReceiver, 0 }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &SenderAndReceiver::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *SenderAndReceiver::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *SenderAndReceiver::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_SenderAndReceiver))
        return static_cast<void*>(const_cast< SenderAndReceiver*>(this));
    return QObject::qt_metacast(_clname);
}

int SenderAndReceiver::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QObject::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        switch (_id) {
        case 0: mySignal(); break;
        case 1: mySignal((*reinterpret_cast< double(*)>(_a[1]))); break;
        case 2: mySignal((*reinterpret_cast< QString(*)>(_a[1]))); break;
        case 3: mySlot(); break;
        case 4: mySlot((*reinterpret_cast< double(*)>(_a[1]))); break;
        case 5: mySlot((*reinterpret_cast< QString(*)>(_a[1]))); break;
        default: ;
        }
        _id -= 6;
    }
    return _id;
}

// SIGNAL 0
void SenderAndReceiver::mySignal()
{
    QMetaObject::activate(this, &staticMetaObject, 0, 0);
}

// SIGNAL 1
void SenderAndReceiver::mySignal(double _t1)
{
    void *_a[] = { 0, const_cast<void*>(reinterpret_cast<const void*>(&_t1)) };
    QMetaObject::activate(this, &staticMetaObject, 1, _a);
}

// SIGNAL 2
void SenderAndReceiver::mySignal(QString _t1)
{
    void *_a[] = { 0, const_cast<void*>(reinterpret_cast<const void*>(&_t1)) };
    QMetaObject::activate(this, &staticMetaObject, 2, _a);
}
QT_END_MOC_NAMESPACE
