from RuckusAutoTest.components.lib.AutoConfig import Ctrl
from RuckusAutoTest.components.lib import common_fns as fns

locators = dict(
    tbl = Ctrl(
        "//div[@id='content']/table",
        'htable',
        dict(hdrs = [],), # to be updated later, see _update_locs()
    ),
)

ctrl_order = 'tbl'

def nav_to(obj, force = False):
    obj.navigate_to(obj.MAIN_PAGE, obj.STATUS_DEVICE, force = force)


m = dict(
    locators = locators,
    ctrl_order = ctrl_order,
    nav_to = nav_to,
)


def _update_locs(obj):
    # updating locators according to AP model first
    m['locators']['tbl'].cfg['hdrs'] = obj.status_device_ths


def get(obj, cfg, is_nav = True, order = 'default'):
    _update_locs(obj)
    return fns.get(m, obj, cfg, is_nav, order)


#--------------------------------------------------------
#  PUBLIC METHODS
#--------------------------------------------------------
def get_all(obj):
    return get(obj, {'tbl':{}})['tbl']


