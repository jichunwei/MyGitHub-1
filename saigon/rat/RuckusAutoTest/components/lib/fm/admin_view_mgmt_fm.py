'''
Since this module covers 2 items (views/statuses), all functions are subfix-ed
with item accordingly: ie.
'''

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, set as ac_set, \
         get as ac_get, format_ctrl, cfg_data_flow2
from RuckusAutoTest.components.lib.dev_features import FM as fmft
from RuckusAutoTest.components.lib import common_fns as fns

'''
# Add a status
fmlib.admin_view_mgmt_fm.add_status(fm, {'status':'this is a status'})

# Delete all views/statuses
fmlib.admin_view_mgmt_fm.delete_all_views(fm)
fmlib.admin_view_mgmt_fm.delete_all_statuses(fm)

# Find a view
fmlib.admin_view_mgmt_fm.find_view(fm, dict(view='standalone'))
'''

locators = dict(
    view_tab = Ctrl("//span[.='View']", 'button'),
    status_tab = Ctrl("//span[.='Inventory Status']", 'button'),

    view_tbl = Ctrl(
        dict(tbl = "//div[@label='View']//table[@class='dashboard']",
             nav = "//div[@label='View']//td[@class='pageSelecter']",),
        'ltable',
        dict(hdrs = fmft.view_mgmt_ths,
             links = dict(delete = "//a[.='Delete']", edit = "//a[.='Edit']",)),
    ),
    status_tbl = Ctrl(
        dict(tbl = "//div[@label='Inventory Status']//table[@class='dashboard']",
             nav = "//div[@label='Inventory Status']//td[@class='pageSelecter']",),
        'ltable',
        dict(hdrs = fmft.inv_status_ths,
             links = dict(delete = "//a[.='Delete']", edit = "//a[.='Edit']",)),
    ),
    create_btn = Ctrl("//span[contains(., 'Create New Inventory')][@class='sb']", 'button'),
    status = Ctrl("//input[@id='newStatusTextField']"),
    ok_btn = Ctrl("//input[@id='okNewStatusButton']", 'button'),
)

ctrl_order = '''
[view_tab view_tbl None]
[status_tab
  status_tbl
  [create_btn status ok_btn]
None]
'''


def nav_to(obj, force = False):
    obj.navigate_to(obj.ADMIN, obj.ADMIN_GROUP_MGMT, force = force)


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


#--------------------------------------------------------
#  PUBLIC METHODS
#--------------------------------------------------------
def add_status(obj, cfg):
    ''' cfg: username, password, confirm_password, role '''
    return set(obj, cfg, is_nav = True)


def delete_all_views(obj):
    return _delete_all(obj, tbl = 'view_tbl')


def delete_all_statuses(obj):
    ''' just delete-able ones '''
    return _delete_all(obj, tbl = 'status_tbl')


def find_view(obj, mcfg, op = 'in'):
    return _find(obj, 'view_tbl', mcfg, op)

