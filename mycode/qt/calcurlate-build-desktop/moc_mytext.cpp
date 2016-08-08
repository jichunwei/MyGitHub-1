/****************************************************************************
** Meta object code from reading C++ file 'mytext.h'
**
** Created: Wed Oct 26 12:37:00 2011
**      by: The Qt Meta Object Compiler version 62 (Qt 4.7.0)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../day1/calcultor/mytext.h"
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'mytext.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 62
#error "This file was generated using the moc from 4.7.0. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
static const uint qt_meta_data_Mytext[] = {

 // content:
       5,       // revision
       0,       // classname
       0,    0, // classinfo
      21,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: signature, parameters, type, tag, flags
       8,    7,    7,    7, 0x0a,
      20,    7,    7,    7, 0x0a,
      31,    7,    7,    7, 0x0a,
      42,    7,    7,    7, 0x0a,
      53,    7,    7,    7, 0x0a,
      64,    7,    7,    7, 0x0a,
      75,    7,    7,    7, 0x0a,
      86,    7,    7,    7, 0x0a,
      97,    7,    7,    7, 0x0a,
     108,    7,    7,    7, 0x0a,
     119,    7,    7,    7, 0x0a,
     130,    7,    7,    7, 0x0a,
     144,    7,    7,    7, 0x0a,
     156,    7,    7,    7, 0x0a,
     169,    7,    7,    7, 0x0a,
     186,    7,    7,    7, 0x0a,
     199,    7,    7,    7, 0x0a,
     214,    7,    7,    7, 0x0a,
     227,    7,    7,    7, 0x0a,
     240,    7,    7,    7, 0x0a,
     253,    7,    7,    7, 0x0a,

       0        // eod
};

static const char qt_meta_stringdata_Mytext[] = {
    "Mytext\0\0operation()\0mySlot_0()\0"
    "mySlot_1()\0mySlot_2()\0mySlot_3()\0"
    "mySlot_4()\0mySlot_5()\0mySlot_6()\0"
    "mySlot_7()\0mySlot_8()\0mySlot_9()\0"
    "mySlot_back()\0mySlot_ce()\0mySlot_clr()\0"
    "mySlot_convert()\0mySlot_div()\0"
    "mySlot_equal()\0mySlot_mul()\0mySlot_add()\0"
    "mySlot_sub()\0mySlot_point()\0"
};

const QMetaObject Mytext::staticMetaObject = {
    { &QLineEdit::staticMetaObject, qt_meta_stringdata_Mytext,
      qt_meta_data_Mytext, 0 }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &Mytext::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *Mytext::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *Mytext::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_Mytext))
        return static_cast<void*>(const_cast< Mytext*>(this));
    return QLineEdit::qt_metacast(_clname);
}

int Mytext::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QLineEdit::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        switch (_id) {
        case 0: operation(); break;
        case 1: mySlot_0(); break;
        case 2: mySlot_1(); break;
        case 3: mySlot_2(); break;
        case 4: mySlot_3(); break;
        case 5: mySlot_4(); break;
        case 6: mySlot_5(); break;
        case 7: mySlot_6(); break;
        case 8: mySlot_7(); break;
        case 9: mySlot_8(); break;
        case 10: mySlot_9(); break;
        case 11: mySlot_back(); break;
        case 12: mySlot_ce(); break;
        case 13: mySlot_clr(); break;
        case 14: mySlot_convert(); break;
        case 15: mySlot_div(); break;
        case 16: mySlot_equal(); break;
        case 17: mySlot_mul(); break;
        case 18: mySlot_add(); break;
        case 19: mySlot_sub(); break;
        case 20: mySlot_point(); break;
        default: ;
        }
        _id -= 21;
    }
    return _id;
}
QT_END_MOC_NAMESPACE
