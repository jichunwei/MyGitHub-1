'''
RESOURCE REFS
. role: FM.roles
'''
from RuckusAutoTest.common.utils import *
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, set as ac_set, \
         get as ac_get, format_ctrl, cfg_data_flow2
from RuckusAutoTest.components.lib.dev_features import FM as fmft
from RuckusAutoTest.components.lib import common_fns as fns


'''
# Add a user
usr_cfg= dict(
    username='luan', password='abc',confirm_password='abc',
    role='Network Administrator')
fmlib.admin_users_fm.add(fm, usr_cfg)

# Delete all user
fmlib.admin_users_fm.delete_all(fm)

# Find a user
fmlib.admin_users_fm.find(fm, dict(username='admin@luannt.com'))

# Edit user
fmlib.admin_users_fm.edit(fm, dict(username='luan'),
                          dict(password='luan',confirm_password='luan',
                               role='Group Administrator'))
'''

locators = dict(
    tbl = Ctrl(
        dict(tbl = "//table[@id='UserList']",
             nav = "//td[@class='pageSelecter']",),
        'ltable',
        dict(hdrs = fmft.user_ths,
             links = dict(delete = "//a[.='Delete']", edit = "//a[.='Edit']",)),
    ),
    create_btn = Ctrl("//div[@id='new-ap']//span[contains(.,'Create')]", 'button'),
    username = Ctrl("//input[@id='txtUserName']"),
    password = Ctrl("//input[@id='txtPass']"),
    confirm_password = Ctrl("//input[@id='txtPass1']"),
    role = Ctrl("//select[@id='selUserRole']", 'select'),
    ok_btn = Ctrl("//input[@id='ok-ap']", 'button'),
)

ctrl_order = '''
[create_btn
  username password confirm_password role
ok_btn]
'''

edit_co = '''
[None
  username password confirm_password role
ok_btn]
'''


def nav_to(obj, force = False):
    obj.navigate_to(obj.ADMIN, obj.ADMIN_USERS, force = force)


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
    add a user
    cfg: username, password, confirm_password, role
    '''
    logging.info('Create a user: %s' % cfg['username'])
    log_cfg(cfg)
    return set(obj, cfg, is_nav = True)


def edit(obj, mcfg, cfg, op = 'eq'):
    '''
    . find the fist-match mcfg (exactly equal)
    . click on edit, update with cfg
    accepted cfg: password, confirm_password, role
    '''
    #r = get_tbl(obj, 'tbl', dict(get='1st',match=mcfg,op=op), is_nav=True)
    r = _find(obj, mcfg, 'tbl', op, is_nav = True)
    if r:
        obj.selenium.click_and_wait(r['links']['edit'])
        set(obj, cfg, is_nav = False, order = edit_co)
        return
    log_cfg(mcfg, 'mcfg')
    log_cfg(cfg, 'cfg')
    raise Exception('Account not found')


def delete(obj, mcfg, op = 'eq'):
    return _delete(obj, mcfg, 'tbl', op)


def delete_all(obj):
    return _delete_all(obj, 'tbl')


def find(obj, mcfg, op = 'eq'):
    r = _find(obj, mcfg, 'tbl', op)
    if r:
        return r['row']
    return None


