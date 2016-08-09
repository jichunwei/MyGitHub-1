from RuckusAutoTest.components.lib.AutoConfig import Ctrl
from RuckusAutoTest.components.lib import common_fns as fns


locators = dict(
    ap_tbl = Ctrl(
        "//table[@id='apsummary']",
        'table',
        dict(hdrs = ['mac', 'desc', 'model', 'status', 'mesh', 'ip', 'vlan',
                     'clients', 'action']),
    ),
)

ctrl_order = '''
ap_tbl
'''

def nav_to(obj, force = False):
    obj.navigate_to(obj.MONITOR, obj.MONITOR_ACCESS_POINTS, force = force)


m = dict(
    locators = locators,
    ctrl_order = ctrl_order,
    nav_to = nav_to,
)

def set(obj, cfg, is_nav = True, order = 'default'):
    return fns.set(m, obj, cfg, is_nav, order)

def get(obj, cfg, is_nav = True, order = 'default'):
    return fns.get(m, obj, cfg, is_nav, order)

def get_tbl(obj, tbl, cfg, is_nav = False, order = None):
    return fns.get_tbl(m, obj, tbl, cfg, is_nav, order)

def _delete_all(obj, tbl = 'tbl'):
    return fns._delete_all(m, obj, tbl)

def _delete(obj, mcfg, tbl = 'tbl', op = 'eq'):
    return fns._delete(m, obj, mcfg, tbl = 'tbl', op = 'eq')

def _find(obj, mcfg, tbl = 'tbl', op = 'eq'):
    return fns._find(m, obj, mcfg, tbl = 'tbl', op = 'eq')

