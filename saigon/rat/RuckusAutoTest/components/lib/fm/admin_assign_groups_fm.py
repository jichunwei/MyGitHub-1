from RuckusAutoTest.common.utils import *
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, set as ac_set, \
         get as ac_get, format_ctrl, cfg_data_flow2
from RuckusAutoTest.components.lib.dev_features import FM as fmft
from RuckusAutoTest.components.lib import common_fns as fns


'''

'''

# not cover the check on table headers yet, but will be...
locators = dict(
    tbl = Ctrl(
        dict(tbl = "//table[@id='UserList']",
             nav = "//div[@id='div-UserList']//td[@class='textAlignRight']",),
        'ltable',
        dict(hdrs = ['username', 'role', 'action'],
             links = dict(assign = "//a[.='Assign Group']")),
    ),
    assign_tbl = Ctrl(
        dict(tbl = "//table[@id='GroupList']",
             nav = "//fieldset[@id='div-GroupList']" + 
                 "//table[preceding-sibling::div/table[@id='GroupList']]" + 
                 "//td[@class='textAlignRight']",),
        'ltable',
        dict(hdrs = ['chk', 'groupname', 'action'],
             links = dict(chk = "//input[@type='checkbox']",
                        details = "//a[.='Details']")),
    ),
    ok_btn = Ctrl("//input[@id='btnOK']", 'button'),
)

ctrl_order = '''
[tbl assign_tbl]
'''


def nav_to(obj, force = False):
    obj.navigate_to(obj.ADMIN, obj.ADMIN_ASSIGN_GROUP_OWNERS, force = force)


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
def assign(obj, cfg):
    '''
    cfg:
    . username: name of user
    . groupnames: name of groups
    '''
    logging.info('Assign groups to user %s' % cfg['username'])
    log_cfg(cfg)
    gn_matches = [dict(groupname = gn) for gn in cfg['groupnames']]
    p = dict(
        tbl = dict(link = 'assign', matches = [dict(username = cfg['username'])], ops = 'eq'),
        assign_tbl = dict(link = 'chk', matches = gn_matches, ops = 'eq'),
    )
    log_cfg(p)
    return set(obj, p)


def get_assigned_groups(obj, username, op = 'eq'):
    '''
    cfg:
    . groupname
    returning checked rows only
    '''
    p = dict(
        tbl = dict(link = 'assign', matches = [dict(username = username)], ops = op),
        assign_tbl = dict(get = 'iter'),
    )
    tbl = [r['row'] for r in get(obj, p)['assign_tbl']
                    if obj.selenium.is_checked(r['links']['chk'])]
    nav_to(obj, force = True) # avoid side effect
    return tbl

