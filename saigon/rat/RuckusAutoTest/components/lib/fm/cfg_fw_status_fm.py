from RuckusAutoTest.common.utils import *
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, set as ac_set, \
         get as ac_get, format_ctrl, cfg_data_flow2
from RuckusAutoTest.components.lib.dev_features import FM as fmft
from RuckusAutoTest.components.lib import common_fns as fns


locators = dict(
    tbl = Ctrl(
        dict(tbl = "//table[@id='firmwaretableList']",
             nav = "//td[@class='pageControlSeperator']",),
        'ltable',
        dict(hdrs = fmft.fw_status_ths,),
    ),
)

ctrl_order = '''tbl'''


def nav_to(obj, force = False):
    obj.navigate_to(obj.PROVISIONING, obj.PROV_FIRMWARE_STATUS, force = force)


m = dict(
    locators = locators,
    ctrl_order = ctrl_order,
    nav_to = nav_to,
)

def get(obj, cfg, is_nav = True, order = 'default'):
    return fns.get(m, obj, cfg, is_nav, order)

def get_tbl(obj, tbl, cfg, is_nav = False, order = None):
    return fns.get_tbl(m, obj, tbl, cfg, is_nav, order)


#--------------------------------------------------------
#  PUBLIC METHODS
#--------------------------------------------------------
def get_all(obj):
    return get_tbl(obj, 'tbl', {}, is_nav = True)

