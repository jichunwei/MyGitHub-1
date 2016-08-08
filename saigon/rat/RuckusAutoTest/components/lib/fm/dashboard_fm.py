import time

from RuckusAutoTest.components.lib.AutoConfig import Ctrl
from RuckusAutoTest.components.lib.dev_features import FM as fmft
from RuckusAutoTest.components.lib import common_fns as fns


locators = dict(
    zd_refresh_btn = Ctrl("//img[@id='zdcmdrefresh']", 'button'),
    zd_loading_ind = Ctrl("//img[@id='zd.loadImg']", 'loading_ind'),
    zd_tbl = Ctrl(
        dict(tbl = "//table[@id='zdtableList']",
             nav = "//table[@id='zdpageContrl']",
        ), 'ltable',
        dict(hdrs = fmft.zd_device_view_ths,
             links = dict(conn = "//a[.='']",
                        disconn = "//a[.='']",),)
    ),

    ap_refresh_btn = Ctrl("//img[@id='deviceviewcmdrefresh']", 'button'),
    ap_loading_ind = Ctrl("//img[@id='deviceview.loadImg']", 'loading_ind'),
    ap_tbl = Ctrl(
        dict(tbl = "//table[@id='deviceviewtableList']",
             nav = "//table[@id='deviceviewpageContrl']",
        ), 'ltable',
        dict(hdrs = fmft.ap_device_view_ths,
             links = dict(conn = "//a[.='']",
                        disconn = "//a[.='']",),)
    ),
)


ctrl_order = '''
[zd_refresh_btn [zd_loading_ind zd_tbl None] None]
[ap_refresh_btn [ap_loading_ind ap_tbl None] None]
'''


def nav_to(obj, force = False):
    obj.navigate_to(obj.DASHBOARD, obj.NOMENU, force = force)
    time.sleep(10) # this page takes long time to load


m = dict(
    locators = locators,
    ctrl_order = ctrl_order,
    nav_to = nav_to,
)

def set(obj, cfg, is_nav = True, order = 'default'):
    return fns.set(m, obj, cfg, is_nav, order)

def get(obj, cfg, is_nav = True, order = 'default'):
    return fns.get(m, obj, cfg, is_nav, order)

def get_tbl(obj, tbl, cfg, is_nav = True, order = 'default'):
    return fns.get_tbl(m, obj, tbl, cfg, is_nav, order)


#--------------------------------------------------------
#  PUBLIC METHODS
#--------------------------------------------------------
def get_view(obj, view, tbl = 'ap_tbl'):
    '''
    . get the view info, it can be a row on zd device view tbl or ap dv tbl
    . since the view can be defined on Inventory > New Search so the tbl is
      required here
    input
    . view: refer to fmft.predef_views, or user-defined
    . tbl:  ap_tbl/zd_tbl
    '''
    if view in fmft.predef_views: # predefined view
        view = fmft.predef_views[view]
    return get_tbl(obj, tbl, dict(get = '1st', match = dict(view = view)))['row']

