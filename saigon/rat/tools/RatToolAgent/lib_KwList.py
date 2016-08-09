import sys, re, types

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

def asDict(aList=None):
   _dict = {}
   if not aList:
      aList = sys.argv[1:]

   for kv in aList:
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
            _dict[_m1] = strStr(_m2)
      else:
         _dict[kv] = None

   return _dict


def strStr(str):
   if len(str) < 3: return str

   c0 = str[0]
   c1 = str[len(str)-1]
   if c0 == c1 and re.match("['\"]", c0):
      return str[1:len(str)-1]
   elif FALSE.match(str):
      return False
   elif TRUE.match(str):
      return True

   try:
      aStruct = eval(str)
      return aStruct
   except:
      return str


def pdict(_dict, name={}):
   _l = 0
   for _k in _dict.keys():
      if len(_k) > _l: _l = len(_k)
   _l = _l + 2
   _fmt = "%%%ds = %%s  %%s" % _l

   if name: print name
   for _k in sorted(_dict.keys()):
      print _fmt % (_k, _dict[_k], type(_dict[_k]))
   print ""


def pKwList(name, **kws):
   _dict = {}
   _dict.update(kws)
   pdict(_dict, name)

# Examples:
#
#   python getKwList.py host=10.32.10.250 int=1 helo long=23L float=0.2 file=/log/log.log
#   python getKwList.py true=True false=False int=3 str=\'3\' line="enter command> "
#

if __name__ == "__main__":
   # _dict = asDict( )
   _dict = asDict( sys.argv[1:] )
   pdict(_dict, "\nCommand arguments as dictionary:\n")

   pKwList ("\nCommand arguments in keyword list:\n", **_dict)

