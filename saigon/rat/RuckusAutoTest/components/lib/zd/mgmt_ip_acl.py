'''
Created on 2010-7-8

@author: cwang@ruckuswireless.com
'''
import time
import copy
import logging

from RuckusAutoTest.components.lib import AutoConfig as ac
from RuckusAutoTest.components.lib.AutoConfig import Ctrl
from RuckusAutoTest.common.utils import compare_dict_key_value

locators = dict(
    tbl=Ctrl(dict(tbl = r"//table[@id='mgmtipacl']",
                  nav = r"//table[@id='mgmtipacl']/tfoot",
                  search = r"//table[@id='user']/tfoot//input[@type='text']",
#                  total = r"//div[@id='actions-user']/span",
                  check_all = r"//input[@id='mgmtipacl-sall']",
                  delete = r"//input[@id='del-mgmtipacl']",
                  ),
            'ltable',
            dict(hdrs = [None, 'name', 'type',],
                 links = dict(edit = r"//span[@id='edit-mgmtipacl-%s']",
                              clone = r"//span[@id='clone-mgmtipacl-%s']",
                              check = r"//input",
                              ),
                )
            ),
    create_btn = Ctrl(r"//span[@id='new-mgmtipacl']", 'button'),
    ip_name = Ctrl(r"//input[@id='ip-acl-name']"),
    single_radio = Ctrl(r"//input[@id='type_single']", "radio"),
    single_addr1 = Ctrl(r"//input[@id='single-addr1']"),
    
    range_radio = Ctrl(r"//input[@id='type_range']", "radio"),
    range_addr1 = Ctrl(r"//input[@id='range-addr1']"),
    range_addr2 = Ctrl(r"//input[@id='range-addr2']"),
    
    subnet_radio = Ctrl(r"//input[@id='type_subnet']", "radio"),
    subnet_addr1 = Ctrl(r"//input[@id='subnet-addr1']"),
    subnet_addr2 = Ctrl(r"//input[@id='subnet-addr2']"),
    
    ok_btn = Ctrl(r"//input[@id='ok-mgmtipacl']", 'button'),
    cancel_btn = Ctrl(r"//input[@id='cancel-mgmtipacl']", 'button'),
    
    #Add locator for management ipv6 acl.
    ipv6_acl_tbl=Ctrl(dict(tbl = r"//table[@id='mgmtipv6acl']",
                           nav = r"//table[@id='mgmtipv6acl']/tfoot",
                           check_all = r"//input[@id='mgmtipv6acl-sall']",
                           delete = r"//input[@id='del-mgmtipv6acl']",
                           ),
                      'ltable',
                      dict(hdrs = [None, 'name', 'ipv6_addr',],
                           links = dict(edit = r"//span[@id='edit-mgmtipv6acl-%s']",
                                        clone = r"//span[@id='clone-mgmtipv6acl-%s']",
                                        check = r"//input",
                                        ),
                           )
                      ),
                
    ipv6_acl_create_btn = Ctrl(r"//span[@id='new-mgmtipv6acl']", 'button'),
    ipv6_acl_name = Ctrl(r"//input[@id='ipv6-acl-name']"),
    ipv6_acl_single_radio = Ctrl(r"//input[@id='typev6_single']", "radio"),
    ipv6_acl_single_addr = Ctrl(r"//input[@id='single-addr1-ipv6']"),
    
    ipv6_acl_prefix_radio = Ctrl(r"//input[@id='typev6_prefix']", "radio"),
    ipv6_acl_prefix_addr = Ctrl(r"//input[@id='prefix-addr1-ipv6']"),
    ipv6_acl_prefix_len = Ctrl(r"//input[@id='prefix-len']"),
    
    ipv6_acl_ok_btn = Ctrl(r"//input[@id='ok-mgmtipv6acl']", 'button'),
    ipv6_acl_cancel_btn = Ctrl(r"//input[@id='cancel-mgmtipv6acl']", 'button'),
)

create_single_mgmtipacl_order = ['create_btn', 'ip_name', 'single_radio', 'single_addr1', 'ok_btn']
create_range_mgmtipacl_order = ['create_btn', 'ip_name', 'range_radio', 'range_addr1', 'range_addr2', 'ok_btn']
create_subnet_mgmtipacl_order = ['create_btn', 'ip_name','subnet_radio', 'subnet_addr1', 'subnet_addr2', 'ok_btn']

edit_single_mgmtipacl_order = ['ip_name', 'single_radio', 'single_addr1', 'ok_btn']
edit_range_mgmtipacl_order = ['ip_name', 'range_radio', 'range_addr1', 'range_addr2', 'ok_btn']
edit_subnet_mgmtipacl_order = ['ip_name','subnet_radio', 'subnet_addr1', 'subnet_addr2', 'ok_btn']

order = dict(c_o = create_single_mgmtipacl_order,
             e_o = edit_single_mgmtipacl_order,
             )

#Define orders for ipv6 mgmt acl.
ipv6_acl_create_single_order = ['ipv6_acl_create_btn', 'ipv6_acl_name', 'ipv6_acl_single_radio', 'ipv6_acl_single_addr', 'ipv6_acl_ok_btn']
ipv6_acl_create_prefix_order = ['ipv6_acl_create_btn', 'ipv6_acl_name','ipv6_acl_prefix_radio', 'ipv6_acl_prefix_addr', 'ipv6_acl_prefix_len', 'ipv6_acl_ok_btn']
ipv6_acl_edit_single_order = ['ipv6_acl_name', 'ipv6_acl_single_radio', 'ipv6_acl_single_addr', 'ipv6_acl_ok_btn']
ipv6_acl_edit_prefix_order = ['ipv6_acl_name','ipv6_acl_prefix_radio', 'ipv6_acl_prefix_addr', 'ipv6_acl_prefix_len', 'ipv6_acl_ok_btn']

ipv6_acl_order = dict(c_o = ipv6_acl_create_single_order,
                      e_o = ipv6_acl_edit_single_order,
                      )
#Access methods
def get_mgmtipacl(zd, name, is_nav = True):
    '''
    This function is to get the information of a user on ZD.
    Input:
    - name: name of the mgmt IP access control which you want to get
    Output:
        A dictionary as below:
        {
            'name': 'mgmt access control name',            
            'type': 'single addr|range addr|subnet addr(e.g 192.168.0.3|192.168.0.3-192.168.0.253|192.168.0.2/24)',
        }
    '''
    if is_nav:
        _nav_to(zd)
    
    r = _get_row_by_mgmtipacl(zd.s, name)
    if r:
        return r['row']
    
    logging.info("mgmt access control [%s] not found" % name)
    return None


def get_all_mgmtipacl(zd, is_nav = True):
    '''
    This function is to get a list of all mgmtipacl on ZD.
    Output:
        A list as below:
        [
         {'name': 'mgmt access control name','type': 'single addr|range addr|subnet addr(e.g 192.168.0.3|192.168.0.3-192.168.0.253|192.168.0.2/24)'},
         {'name': 'mgmt access control name','type': 'single addr|range addr|subnet addr(e.g 192.168.0.3|192.168.0.3-192.168.0.253|192.168.0.2/24)'},
         ...
        ]
    '''
    if is_nav:
        _nav_to(zd)
    
    all_mgmtipacl = []
    for r in _iter_mgmtipacl_tbl(zd.s, locators['tbl']):
        all_mgmtipacl.append(r['row'])        
        
    return all_mgmtipacl



def create_mgmtipacl(zd, cfg = {}, is_nav = True):
    '''
    This function is to create new mgmt access control.
    Input:
    - cfg: a dictionary of config items. Support following keys
        {
            'name': 'mgmt ip acl name',
            'type': 'single|range|subnet,
            'addr': 'single addr|range addr|subnet addr(e.g 192.168.0.3|192.168.0.3-192.168.0.253|192.168.0.2/24)',                        
        }
    Return: no return, raise exception if error.
    '''
    #@ZJ 20141031  fix creating ip-acl failed because of not nav to configure page 
    zd.logout()
    zd.login()
    if is_nav:
        _nav_to(zd)
        time.sleep(1)
    
    _cfg = {'name':'mgmt-ip-acl-test',
            'type':'single',
            'addr':'192.168.0.22',}
    _cfg.update(cfg)
    
    return _create_mgmtipacl(zd.s, _cfg)


def edit_mgmtipacl(zd, oldname, cfg = {}, is_nav = True):
    '''
    This function is to edit an old MGMT ACL.
    Input:
    - olduser: the name of the MGMT ACL which you want to edit.
    - cfg: a dictionary of config items. Support following keys
        {
            'name': 'MGMT IP access control name',
            'type': 'single|range|subnet,
            'addr': 'single addr|range addr|subnet addr(e.g 192.168.0.3|192.168.0.3-192.168.0.253|192.168.0.2/24)',
        }
    Return: no return, raise exception if error.
    ''' 
    if is_nav:
        _nav_to(zd)
    
    _edit_mgmtipacl(zd.s, oldname, cfg)
    logging.info('edit MGMT ACL [%s] successfully!' %oldname)
    

def delete_mgmtipacl(zd, name, is_nav = True):
    """
    This function is to delete a MGMT IP Access Control on ZD.
    Input:
        name: name of the mgmtipacl which you want to delete
    Return: no return, raise exception if error.
    """ 
    if is_nav:
        _nav_to(zd)
    time.sleep(5)
    s, L= zd.s, locators['tbl'].loc
    macl_loc_info = _get_row_by_mgmtipacl(s, name)
    if macl_loc_info:
        s.click_if_not_checked(macl_loc_info['links']['check'])
        s.click_and_wait(L['delete'])
        logging.info('Delete mgmtipacl [%s] successfully' %name)
        return
    
    raise Exception("mgmt ip access control [%s] not found" % name)


def delete_all_mgmtipacl(zd, is_nav = True):
    '''
    This function is to delete all mgmt ip access control on ZD.    
    '''
    if is_nav:
        _nav_to(zd)
        
    s, L = zd.s, locators['tbl'].loc
    s.click_if_not_checked(L['check_all'])
    s.click_and_wait(L['delete'], 4)    
    
    
##Add methods for mgmt-acl-ipv6.
def get_mgmt_ipv6_acl(zd, name, is_nav = True):
    '''
    This function is to get the information of a user on ZD.
    Input:
    - name: name of the mgmt IP access control which you want to get
    Output:
        A dictionary as below:
        {
            'name': 'mgmt access control name',            
            'type': 'single addr|range addr|subnet addr(e.g 192.168.0.3|192.168.0.3-192.168.0.253|192.168.0.2/24)',
        }
    '''
    if is_nav:
        _nav_to(zd)
    
    r = _get_row_by_mgmt_ipv6_acl(zd.s, name)
    if r:
        return r['row']
    
    logging.info("mgmt ipv6 access control [%s] not found" % name)
    return None


def get_all_mgmt_ipv6_acl(zd, is_nav = True):
    '''
    This function is to get a list of all mgmtipacl on ZD.
    Output:
        A list as below:
        [
         {'name': 'mgmt access control name',
         'type': 'single addr|range addr|subnet addr(e.g 192.168.0.3|192.168.0.3-192.168.0.253|192.168.0.2/24)'},
         {'name': 'mgmt access control name',
         'type': 'single addr|range addr|subnet addr(e.g 192.168.0.3|192.168.0.3-192.168.0.253|192.168.0.2/24)'},
         ...
        ]
    '''
    if is_nav:
        _nav_to(zd)
        
    #Wait for page loading.
    time.sleep(20)
    
    all_mgmtipacl = []
    for r in _iter_mgmtipacl_tbl(zd.s, locators['ipv6_acl_tbl']):
        all_mgmtipacl.append(r['row'])        
        
    return all_mgmtipacl

def create_mgmt_ipv6_acl(zd, cfg = {}, is_nav = True):
    '''
    This function is to create new mgmt access control.
    Input:
    - cfg: a dictionary of config items. Support following keys
        {
            'name': 'mgmt ip acl name',
            'type': 'single|prefix,
            'addr': 'single addr|addr and prefix',                        
        }
    Return: no return, raise exception if error.
    '''
    if is_nav:
        _nav_to(zd)
    
    time.sleep(20)
    
    _cfg = {'name':'mgmt-ip-acl-test',
            'type':'single',
            'addr':'2020:db8:1::10',}
    _cfg.update(cfg)
    
    return _create_mgmt_ipv6_acl(zd.s, _cfg)

def edit_mgmt_ipv6_acl(zd, oldname, cfg = {}, is_nav = True):
    '''
    This function is to edit an old MGMT ACL.
    Input:
    - olduser: the name of the MGMT ACL which you want to edit.
    - cfg: a dictionary of config items. Support following keys
        {
            'name': 'MGMT IP access control name',
            'type': 'single|range|subnet,
            'addr': 'single addr|range addr|subnet addr(e.g 192.168.0.3|192.168.0.3-192.168.0.253|192.168.0.2/24)',
        }
    Return: no return, raise exception if error.
    ''' 
    if is_nav:
        _nav_to(zd)
    
    _edit_mgmt_ipv6_acl(zd.s, oldname, cfg)
    logging.info('edit MGMT IPV6 ACL [%s] successfully!' %oldname)
    

def delete_mgmt_ipv6_acl(zd, name, is_nav = True):
    """
    This function is to delete a MGMT IP Access Control on ZD.
    Input:
        name: name of the mgmtipacl which you want to delete
    Return: no return, raise exception if error.
    """ 
    if is_nav:
        _nav_to(zd)
    
    s, L= zd.s, locators['tbl'].loc
    r = _get_row_by_mgmtipacl(s, name)    
    if r:
        s.click_if_not_checked(r['links']['check'])
        s.click_and_wait(L['delete'])
        logging.info('Delete mgmtipacl [%s] successfully' %name)
        return
    
    raise Exception("mgmt ip access control [%s] not found" % name)


def delete_all_mgmt_ipv6_acl(zd, is_nav = True):
    '''
    This function is to delete all mgmt ip access control on ZD.    
    '''
    if is_nav:
        _nav_to(zd)
        
    s, L = zd.s, locators['ipv6_acl_tbl'].loc
    if zd.s.is_element_present(L['check_all']) and zd.s.is_visible(L['check_all']):            
        s.click_if_not_checked(L['check_all'])
        s.click_and_wait(L['delete'], 4) 
    
def compare_mgmt_ipv6_acl_gui_set_get(set_acl_list, get_acl_list):
    set_ipv6_dict = _convert_list_to_dict(set_acl_list, 'name')
    get_ipv6_dict = _convert_list_to_dict(get_acl_list, 'name')
    
    set_get_keys_mapping = {'addr': 'ipv6_addr'}
    pass_items = ['type']
    
    for key, acl_cfg in set_ipv6_dict.items():
        set_ipv6_dict[key] = _convert_dict_with_new_keys(acl_cfg, set_get_keys_mapping)
        
    res = compare_dict_key_value(set_ipv6_dict, get_ipv6_dict, pass_items)
    
    return res

#Protected Method
def _nav_to(zd):
    id = zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SYSTEM)
    try:
        zd.refresh()
    except:
        pass
    
    return id


def _iter_mgmtipacl_tbl(s, ctrl, cfg = {}):
    p = dict(loc=ctrl.loc['tbl'],
             hdrs=ctrl.cfg['hdrs'],
             match=cfg.get('match', {}),
             op=cfg.get('op', 'in'),
             )            
    for r in s.iter_table_rows(**p):
        r['links'] = copy.deepcopy(ctrl.cfg.get('links', {}))
        for k in r['links'].iterkeys():
            if k != 'check':
                r['links'][k] = (r['tmpl'] % r['idx']) + r['links'][k] % (r['idx'] - 1)
            else:
                r['links'][k] = (r['tmpl'] % r['idx']) + r['links'][k]
        yield r


def _get_row_by_mgmtipacl(s, name):    
    cfg = dict(match = dict(name = name,),
               op = 'eq',               
               )
    
    for r in _iter_mgmtipacl_tbl(s, locators['tbl'], cfg):
        return r
    
    return {}


def _set_mgmtipacl(s, cfg, order = []):
    L = locators
    ac.set(s, L, cfg, order)
    s.get_alert(L['cancel_btn'].loc)


def _edit_mgmtipacl(s, oldname, cfg = {}, type = 'edit'):
    ip_type = cfg.pop('type')
    s_cfg = {}
    s_cfg['ip_name'] = cfg['name']
    if ip_type == 'single':
        order['e_o'] = edit_single_mgmtipacl_order        
        s_cfg['single_radio'] = True
        s_cfg['single_addr1'] = cfg['addr']
        
    elif ip_type == 'range':
        order['e_o'] = edit_range_mgmtipacl_order
        s_cfg['range_radio'] = True
        addrs = cfg['addr'].split('-')
        s_cfg['range_addr1'] = addrs[0].strip()
        s_cfg['range_addr2'] = addrs[1].strip()
        
    else:
        order['e_o'] = edit_subnet_mgmtipacl_order
        s_cfg['subnet_radio'] = True
        addrs = cfg['addr'].split('/')
        s_cfg['subnet_addr1'] = addrs[0].strip()
        s_cfg['subnet_addr2'] = addrs[1].strip()
        
    r = _get_row_by_mgmtipacl(s, oldname)
    if r:
        s.click_and_wait(r['links'][type])
        _set_mgmtipacl(s, s_cfg, order['e_o'])
        logging.info('modify mgmt access control [%s] successfully!' % oldname)        
        return
    
    raise Exception(" [%s] not found!" % oldname)
        

def _create_mgmtipacl(s, cfg):
    type = cfg.pop('type')
    s_cfg = {}
    s_cfg['ip_name'] = cfg['name']
    if type == 'single':
        order['c_o'] = create_single_mgmtipacl_order        
        s_cfg['single_radio'] = True
        s_cfg['single_addr1'] = cfg['addr']
        
    elif type == 'range':
        order['c_o'] = create_range_mgmtipacl_order
        s_cfg['range_radio'] = True
        addrs = cfg['addr'].split('-')
        s_cfg['range_addr1'] = addrs[0].strip()
        s_cfg['range_addr2'] = addrs[1].strip()
        
    else:
        order['c_o'] = create_subnet_mgmtipacl_order
        s_cfg['subnet_radio'] = True
        addrs = cfg['addr'].split('/')
        s_cfg['subnet_addr1'] = addrs[0].strip()
        s_cfg['subnet_addr2'] = addrs[1].strip()
        
    _set_mgmtipacl(s, s_cfg, order['c_o'])    
    logging.info('create mgmt ip access control [%s] successfully!' %cfg['name'])
    
#Add new methods for management ipv6 acl.
def _iter_mgmt_ipv6_acl_tbl(s, ctrl, cfg = {}):
    p = dict(loc=ctrl.loc['ipv6_acl_tbl'],
             hdrs=ctrl.cfg['hdrs'],
             match=cfg.get('match', {}),
             op=cfg.get('op', 'in'),
             )            
    for r in s.iter_table_rows(**p):
        r['links'] = copy.deepcopy(ctrl.cfg.get('links', {}))
        for k in r['links'].iterkeys():
            if k != 'check':
                r['links'][k] = (r['tmpl'] % r['idx']) + r['links'][k] % (r['idx'] - 1)
            else:
                r['links'][k] = (r['tmpl'] % r['idx']) + r['links'][k]
        yield r

def _get_row_by_mgmt_ipv6_acl(s, name):    
    cfg = dict(match = dict(name = name,),
               op = 'eq',               
               )
    for r in _iter_mgmt_ipv6_acl_tbl(s, locators['ipv6_acl_tbl'], cfg):
        return r
    return {}

def _set_mgmt_ipv6_acl(s, cfg, order = []):
    L = locators
    ac.set(s, L, cfg, order)
    s.get_alert(L['ipv6_acl_cancel_btn'].loc)

def _edit_mgmt_ipv6_acl(s, oldname, cfg = {}, type = 'edit'):
    ip_type = cfg.pop('type')
    s_cfg = {}
    s_cfg['ip_name'] = cfg['name']
    if ip_type == 'single':
        order['e_o'] = edit_single_mgmtipacl_order        
        s_cfg['ipv6_acl_single_radio'] = True
        s_cfg['ipv6_acl_single_addr'] = cfg['addr']
        
    else:
        order['e_o'] = edit_subnet_mgmtipacl_order
        s_cfg['ipv6_acl_prefix_radio'] = True
        addrs = cfg['addr'].split('/')
        s_cfg['ipv6_acl_prefix_addr'] = addrs[0].strip()
        s_cfg['ipv6_acl_prefix_len'] = addrs[1].strip()
        
    r = _get_row_by_mgmtipacl(s, oldname)
    if r:
        s.click_and_wait(r['links'][type])
        _set_mgmt_ipv6_acl(s, s_cfg, order['e_o'])
        logging.info('modify mgmt ipv6 access control [%s] successfully!' % oldname)        
        return
    
    raise Exception(" [%s] not found!" % oldname)

def _create_mgmt_ipv6_acl(s, cfg):
    type = cfg.pop('type')
    s_cfg = {}
    s_cfg['ipv6_acl_name'] = cfg['name']
    if type == 'single':
        order['c_o'] = ipv6_acl_create_single_order
        s_cfg['ipv6_acl_single_radio'] = True
        s_cfg['ipv6_acl_single_addr'] = cfg['addr']
    else:
        order['c_o'] = ipv6_acl_create_prefix_order
        s_cfg['ipv6_acl_prefix_radio'] = True
        addrs = cfg['addr'].split('/')
        s_cfg['ipv6_acl_prefix_addr'] = addrs[0].strip()
        s_cfg['ipv6_acl_prefix_len'] = addrs[1].strip()
        
    _set_mgmt_ipv6_acl(s, s_cfg, order['c_o'])
    logging.info('create mgmt ipv6 access control [%s] successfully!' %cfg['name'])
    
def _convert_list_to_dict(cfg_list, key_name):
    '''
    Convert dict list to a dict, will use cfg key_name value as key.
    '''     
    cfg_dict = {}
    
    for cfg in cfg_list:
        cfg_dict[cfg[key_name]] = cfg
    
    return cfg_dict

def _convert_dict_with_new_keys(org_dict, keys_mapping):
    '''
    Convert dict replace key with new key based on keys_mapping.
    '''
    new_dict = {}
    
    if keys_mapping:
        for key, value in org_dict.items():
            if keys_mapping.has_key(key):
                new_key = keys_mapping[key]
            else:
                new_key = key
                
            new_dict[new_key] = value
    else:
        new_dict = org_dict
        
    return new_dict
