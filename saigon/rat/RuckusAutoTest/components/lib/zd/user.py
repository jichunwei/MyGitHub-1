import time
import copy
import logging

from RuckusAutoTest.components.lib import AutoConfig as ac
from RuckusAutoTest.components.lib.AutoConfig import Ctrl


locators = dict(
    tbl=Ctrl(dict(tbl = r"//table[@id='user']",
                  nav = r"//table[@id='user']/tfoot",
                  search = r"//table[@id='user']/tfoot//input[@type='text']",
                  total = r"//div[@id='actions-user']/span",
                  check_all = r"//input[@id='user-sall']",
                  delete = r"//input[@id='del-user']",
                  ),
            'ltable',
            dict(hdrs = [None, 'username', 'fullname', 'role'],
                 links = dict(edit = r"//span[@id='edit-user-%s']",
                              clone = r"//span[@id='clone-user-%s']",
                              check = r"//input",
                              ),
                )
            ),
    create_btn = Ctrl(r"//span[@id='new-user']", 'button'),
    username = Ctrl(r"//input[@id='username']"),
    fullname = Ctrl(r"//input[@id='full-name']"),
    password = Ctrl(r"//input[@id='password1']"),
    confirm_password = Ctrl(r"//input[@id='password2']"),
    role = Ctrl(r"//select[@id='roles']", 'select'),
    ok_btn = Ctrl(r"//input[@id='ok-user']", 'button'),
    cancel_btn = Ctrl(r"//input[@id='cancel-user']", 'button'),
)

create_order = ['create_btn', 'username', 'fullname', 'password', 'confirm_password', 'role', 'ok_btn']
edit_order = ['username', 'fullname', 'password', 'confirm_password', 'role', 'ok_btn']

order = dict(c_o = create_order,
             e_o = edit_order,
             )


def get_user(zd, username, is_nav = True):
    '''
    This function is to get the information of a user on ZD.
    Input:
    - username: name of the user which you want to get
    Output:
        A dictionary as below:
        {
            'username': 'user name',
            'fullname': 'full name of this user',
            'role': 'role'
        }
    '''
    if is_nav:
        _nav_to(zd)
    
    r = _get_row_by_username(zd.s, username)
    if r:
        return r['row']
    
    logging.info("User [%s] not found" % username)
    return None


def get_all_users(zd, is_nav = True):
    '''
    This function is to get a list of all users on ZD.
    Output:
        A list as below:
        [
         {'username': 'user name','fullname': 'full name of this user','role': 'role'},
         {'username': 'user name','fullname': 'full name of this user','role': 'role'},
         ...
        ]
    '''
    if is_nav:
        _nav_to(zd)
    
    all_user = []
    for r in _iter_user_tbl(zd.s, locators['tbl']):
#        all_user.append([r['row']])
        all_user.append(r['row'])        
        
    return all_user

def get_all_users_total_number(zd, is_nav = True):
    '''
    Go to users list, catch total number of users.
    '''
    if is_nav:
        _nav_to(zd)
    locator = zd.info['loc_cfg_user_total_number_span']
    zd._wait_for_element(locator)
    user_total = zd._get_total_number(locator, "Users")
    return user_total
    

def delete_user(zd, username, is_nav = True):
    """
    This function is to delete a user on ZD.
    Input:
        username: name of the user which you want to delete
    Return: no return, raise exception if error.
    """ 
    if is_nav:
        _nav_to(zd)
    
    s, L= zd.s, locators['tbl'].loc
    r = _get_row_by_username(s, username)    
    if r:
        s.click_if_not_checked(r['links']['check'])
        s.click_and_wait(L['delete'])
        logging.info('Delete user [%s] successfully' %username)
        return
    
    raise Exception("User [%s] not found" % username)


def delete_all_users(zd, is_nav = True):
    '''
    This function is to delete all users on ZD.
    Return: number of users have been deleted.
    '''
    if is_nav:
        _nav_to(zd)
        
    s, L = zd.s, locators['tbl'].loc

    _set_search_box(s, L['search'], '')
    
    if zd._wait_for_element(L['total']):
        total = int(zd._get_total_number(L['total'], "Users"))
    else:
        raise Exception('Have not found element %s' % L['total'])
    
    t = total
    while t > 0:
        s.click_if_not_checked(L['check_all'])
        s.click_and_wait(L['delete'], 4)
        zd._wait_for_element(L['total'])
        t = int(zd._get_total_number(L['total'], "Users"))
        
    return total


def create_user(zd, cfg = {}, is_nav = True):
    '''
    This function is to create new users.
    Input:
    - cfg: a dictionary of config items. Support following keys
        {
            'username': 'user name',
            'fullname': 'full name of this user',
            'password': 'password',
            'confirm_password': 'password',
            'role': 'Default' | 'Role name',
            'number': number of users want to create
        }
    Return: no return, raise exception if error.
    '''
    if is_nav:
        _nav_to(zd)
    
    _cfg = {'number':1,}
    _cfg.update(cfg)
    
    return _create_user(zd.s, _cfg)


def edit_user(zd, oldname, cfg = {}, is_nav = True):
    '''
    This function is to edit an old user.
    Input:
    - olduser: the name of the user which you want to edit.
    - cfg: a dictionary of config items. Support following keys
        {
            'username': 'user name',
            'fullname': 'full name of this user',
            'password': 'password',
            'confirm_password': 'password',
            'role': 'Default' | 'Role name'
        }
    Return: no return, raise exception if error.
    ''' 
    if is_nav:
        _nav_to(zd)
    
    _edit_user(zd.s, oldname, cfg)
    logging.info('edit user [%s] successfully!' %oldname)
    

def clone_user(zd, oldname, cfg = {}, is_nav = True):
    '''
    This function is to clone an old user.
    Input:
    - olduser: the name of the user which you want to clone.
    - cfg: a dictionary of config items. Support following keys
        {
            'username': 'user name',
            'fullname': 'full name of this user',
            'password': 'password',
            'confirm_password': 'password',
            'role': 'Default' | 'Role name'
        }
    Return: no return, raise exception if error.
    '''
    if is_nav:
        _nav_to(zd)

    _edit_user(zd.s, oldname, cfg, 'clone')
    logging.info('clone user [%s] to user [%s] successfully!' %(oldname, cfg['username']))
    
    
def _nav_to(zd):
    return zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_USERS)


def _set_search_box(s, loc, v):
    s.type_text(loc, v)
    ENTER_CODE = u'\013'
    s.key_down(loc, ENTER_CODE)
    time.sleep(2.5)


def _iter_user_tbl(s, ctrl, cfg = {}):
    p = dict(loc=ctrl.loc['tbl'],
             hdrs=ctrl.cfg['hdrs'],
             match=cfg.get('match', {}),
             op=cfg.get('op', 'in'),
             )
    
    _set_search_box(s, ctrl.loc['search'], cfg.get('search', ''))
    
    for page in s.iter_tbl_pages(ctrl.loc['nav']):
        for r in s.iter_table_rows(**p):
            r['links'] = copy.deepcopy(ctrl.cfg.get('links', {}))
            for k in r['links'].iterkeys():
                if k != 'check':
                    r['links'][k] = (r['tmpl'] % r['idx']) + r['links'][k] % (r['idx'] - 1)
                else:
                    r['links'][k] = (r['tmpl'] % r['idx']) + r['links'][k]
            yield r


def _get_row_by_username(s, username):    
    cfg = dict(match = dict(username = username,),
               op = 'eq',
               search = username,
               )
    
    for r in _iter_user_tbl(s, locators['tbl'], cfg):
        return r
    
    return {}


def _set_user(s, cfg, order = []):
    L = locators
    ac.set(s, L, cfg, order)
    s.get_alert(L['cancel_btn'].loc)


def _create_user(s, cfg):    
    num = cfg.pop('number')
    if num > 1:
        username = cfg.get('username', '')
        for i in range(num):
            cfg['username'] = '%s_%d' % (username, i)
            _set_user(s, cfg, order['c_o'])
            logging.info('create user [%s] successfully!' %cfg['username'])
    else:
        _set_user(s, cfg, order['c_o'])
        logging.info('create user [%s] successfully!' %cfg['username'])

 
def _edit_user(s, oldname, cfg = {}, type = 'edit'):       
    r = _get_row_by_username(s, oldname)
    if r:
        s.click_and_wait(r['links'][type])
        _set_user(s, cfg, order['e_o'])
        return
    
    raise Exception("User [%s] not found!" % oldname)
