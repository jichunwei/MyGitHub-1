"""
from rat directory invoke python, then do

from u.zdcli import demote as dg
dg.demo()
"""

from RuckusAutoTest.components.lib.zdcli.output_as_dict import *
import wlaninfo_demo_data as DATA

def phdr(hdrline):
    _dash = "-" * (2+len(hdrline))
    print "+%s+" % _dash
    print "| %s |" % hdrline
    print "+%s+" % _dash

def demo(return_result=False,list_sep=None):
   _R = parse(DATA._mocked_ap_info,list_sep=list_sep)
   phdr("output from ZD cmd: wlaninfo -A -l3")
   print DATA._mocked_ap_info
   phdr("python dict after parsing displayed using pformat(result,2,120)")
   print pformat(_R,2,120)
   if return_result:
       return _R
   return None

def demogroup(debug=False,list_sep=None):
    _glist = parse_as_grouplist(DATA._mocked_ap_info,debug=debug,list_sep=list_sep)
    print pformat(_glist,2,120)
    return _glist


