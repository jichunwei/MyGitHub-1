import copy
import logging

from RuckusAutoTest.common.utils import log_cfg
#from RuckusAutoTest.components.lib import AutoConfig as ac
from RuckusAutoTest.components.lib.AutoConfig import (
        Ctrl, #format_ctrl, cfg_data_flow2
)
from RuckusAutoTest.components.lib.dev_features import FM as fmft
from RuckusAutoTest.components.lib import common_fns as fns


# not cover the check on table headers yet, but will be...
locators = dict(
    tbl = Ctrl(
        dict(tbl = "//table[@id='GroupList']",
             nav = "//div[@id='div-GroupList']//td[@class='pageSelecter']",),
        'ltable',
        dict(hdrs = fmft.device_assignment_ths,
             links = dict(delete = "//a[.='Delete']",
                        edit = "//a[.='Edit']",
                        assign = "//a[.='Assign Devices']")),
    ),
    create_btn = Ctrl("//div[@id='new-ap']//span[contains(.,'Create')]", 'button'),
    groupname = Ctrl("//input[@id='txtGroupName']"),
    ok_btn = Ctrl("//input[@id='ok-ap']", 'button'),
    # assign devices
    reg_tbl = Ctrl(
        dict(tbl = "//table[@id='AllDeviceList']",
             nav = "//table[preceding-sibling::table[@id='AllDeviceList']]" +
                 "//td[@class='pageSelecter']",),
        'ltable',
        dict(hdrs = ['chk', 'serial', 'model'],
             links = dict(chk = "//input[@type='checkbox']",)),
    ),
    assign_tbl = Ctrl(
        dict(tbl = "//table[@id='AssignedDeviceList']",
             nav = "//table[preceding-sibling::table[@id='AssignedDeviceList']]" +
                 "//td[@class='pageSelecter']",),
        'ltable',
        dict(hdrs = ['chk', 'serial', 'model'],
             links = dict(chk = "//input[@type='checkbox']",)),
    ),
    add_btn = Ctrl("//a[@id='btnAdd']", 'button'),
    rem_btn = Ctrl("//a[@id='btnRemove']", 'button'),
    assign_btn = Ctrl("//input[@value='Assign']", 'button'),
)

ctrl_order = '''
[create_btn groupname ok_btn]
[tbl
  [None reg_tbl add_btn]
  [None assign_tbl rem_btn]
None]
'''


def nav_to(obj, force = False):
    obj.navigate_to(obj.ADMIN, obj.ADMIN_MANAGED_DEVICE_ASSIGNMENT, force = force)


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

def _find(obj, mcfg, tbl = 'tbl', op = 'eq', is_nav = False):
    return fns._find(m, obj, mcfg, tbl = 'tbl', op = 'eq', is_nav = False)


#--------------------------------------------------------
#  PUBLIC METHODS
#--------------------------------------------------------
def add(obj, cfg):
    '''
    add an device assignment
    . create a group
    . click on that group to assign devices
    . assign the selected devices to that group (supporting both by serial and model)
    cfg:
    . groupname
    . [matches]: list of devices (by serial or model) as a 'matches' config
      i.e [dict(model='zf2942'), dict(model='zd1006')]
    '''
    logging.info('Create a group: %s' % cfg['groupname'])
    log_cfg(cfg)
    cfg = copy.deepcopy(cfg)
    p1 = dict(groupname = cfg['groupname'])
    set(obj, p1)
    if 'matches' in cfg:
        p2 = dict(
            tbl = dict(link = 'assign', matches = [p1], ops = 'eq'), # getting group
            reg_tbl = dict(link = 'chk', matches = cfg['matches'], ops = 'eq'),
            #add_btn=None,
        )
        logging.info('[optional] Assign devices to created group')
        log_cfg(p2)
        return set(obj, p2)


def get_assigned_devices(obj, groupname, op = 'eq'):
    '''
    cfg:
    . groupname
    '''
    p = dict(
        tbl = dict(link = 'assign', matches = [dict(groupname = groupname)], ops = op),
        assign_tbl = dict(get = 'all'),
    )
    tbl = get(obj, p)['assign_tbl']
    nav_to(obj, force = True) # ignore side effect
    return tbl


def delete_all(obj):
    return _delete_all(obj, 'tbl')


def find(obj, mcfg, op = 'eq'):
    r = _find(obj, mcfg, 'tbl', op)
    if r:
        return r['row']
    return None

