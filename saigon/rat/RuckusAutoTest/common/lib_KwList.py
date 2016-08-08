import sys
import re
import types

PATTERN = re.compile(r'([^=]+)=(.*)')
INTEGER = re.compile(r'^\d+$')
LONG = re.compile(r'^\d+L$')
FLOAT1 = re.compile(r'^\d*\.\d+$')
FLOAT2 = re.compile(r'^\d+\.\d*$')
NONE = re.compile(r'^(|false|none|\s+)$', re.I)
TRUE = re.compile(r'^true$', re.I)
FALSE = re.compile(r'^(false|none)$', re.I)
TUPLE = re.compile(r'^\(.*\)$')
LIST = re.compile(r'^\[.*\]$')

def as_dict(a_list = None):
    _dict = {}
    if not a_list:
        a_list = sys.argv[1:]

    for kv in a_list:
        m = PATTERN.match(kv)
        if m:
            _m1 = m.group(1)
            _m2 = m.group(2)
            # print "%s --> {%s} = {%s}" % (kv, _m1, _m2)
            _none = NONE.match(_m2)
            if _none:
                _dict[_m1] = None
            elif FLOAT1.match(_m2) or FLOAT2.match(_m2):
                _dict[_m1] = float(_m2)
            elif LONG.match(_m2):
                _dict[_m1] = long(_m2)
            elif INTEGER.match(_m2):
                _dict[_m1] = int(_m2)
            elif TUPLE.match(_m2):
                _dict[_m1] = eval(_m2)
            elif LIST.match(_m2):
                _dict[_m1] = eval(_m2)
            else:
                # _dict[_m1] = _m2
                _dict[_m1] = str_str(_m2)
        else:
            _dict[kv] = None

    return _dict


def str_str(str):
    if len(str) < 3: return str

    c0 = str[0]
    c1 = str[len(str) - 1]
    if c0 == c1 and re.match("['\"]", c0):
        return str[1:len(str) - 1]
    elif FALSE.match(str):
        return False
    elif TRUE.match(str):
        return True

    try:
        a_struct = eval(str)
        return a_struct
    except:
        return str


def p_dict(_dict, name = {}):
    _l = 0
    for _k in _dict.keys():
        if len(_k) > _l: _l = len(_k)
    _l = _l + 2
    _fmt = "%%%ds = %%s  %%s" % _l

    if name: print name
    for _k in sorted(_dict.keys()):
        print _fmt % (_k, _dict[_k], type(_dict[_k]))
    print ""


def p_kwlist(name, **kws):
    _dict = {}
    _dict.update(kws)
    p_dict(_dict, name)

# Examples:
#    python getKwList.py host=10.32.10.250 int=1 helo long=23L float=0.2 file=/log/log.log
#    python getKwList.py true=True false=False int=3 str=\'3\' line="enter command> "
#

if __name__ == "__main__":
    # _dict = as_dict( )
    _dict = as_dict(sys.argv[1:])
    p_dict(_dict, "\nCommand arguments as dictionary:\n")

    p_kwlist ("\nCommand arguments in keyword list:\n", **_dict)

