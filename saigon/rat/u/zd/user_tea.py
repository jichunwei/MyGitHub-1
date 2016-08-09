'''
Do some action related to Users table in ZD(create/edit/clone/get/get_all/delete/delete_all).
    + Create:
        + Go to Configure > Users.
        + Click on "Create New" link.
        + Configure a user according to your input configuration.
        + Click on "OK" button.

    + Edit:
        + Go to Configure > Users.
        + Input the name of the user you want to edit to the search box and click enter.
        + If the user exists, click on "Edit" link of the user.
        + Edit the user according to your input configuration.
        + Click on "OK" button.

    + Clone:
        + Go to Configure > Users.
        + Input the name of the user you want to clone to the search box and click enter.
        + If the user exists, click on "Clone" link of the user.
        + Configure the user according to your input configuration.
        + Click on "OK" button.

    + Get:
        + Go to Configure > Users.
        + Input the name of the user you want to get to the search box and click enter.
        + If the user exists, return the information of the user.

    + Get_all:
        + Go to Configure > Users.
        + Clear the search box.
        + Return the information of all users. 

    + Delete:
        + Go to Configure > Users.
        + Input the name of the user you want to delete to the search box and click enter.
        + If the user exists, check the check box of the user.
        + Click on "Delete" button.

    + Delete_all:
        + Go to Configure > Users.
        + Clear the search box.
        + Delete all users by page using the check box in the head of the table. 
        
Examples: 
tea.py u.zd.user_tea action=create username=ruckus password=12345 confirm_password=12345
tea.py u.zd.user_tea action=create username=ruckus fullname=ruckus.sdc password=abcde confirm_password=abcde role=ruckus number=500
tea.py u.zd.user_tea action=edit user=ruckus username=wireless fullname=wireless.sdc password=12345 confirm_password=12345 role=ruckus
tea.py u.zd.user_tea action=clone user=ruckus username=wireless fullname=wireless.sdc password=12345 confirm_password=12345 role=ruckus
tea.py u.zd.user_tea action=get user=ruckus
tea.py u.zd.user_tea action=get_all
tea.py u.zd.user_tea action=delete user=ruckus
tea.py u.zd.user_tea action=delete_all
'''


import copy
import logging

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)

from RuckusAutoTest.components.lib.zd import user


default_cfg = dict(zd_ip_addr = '192.168.0.2')


def do_config(cfg):
    _cfg = default_cfg
    _cfg.update(cfg)
    
    if not _cfg.has_key('action'):
        raise Exception('please provide your action["create", "edit", "clone", "get", "get_all", "delete", "delete_all"]')
    
    elif not _cfg['action']:
        raise Exception("action's value is empty")
    
    _user_cfg = copy.deepcopy(cfg)
    ks = _user_cfg.keys()
    for k in ks:
        value = _is_user_info(k)
        if not value:
            _user_cfg.pop(k)
    _cfg['user_cfg'] = _user_cfg
    
    _cfg['zd'] = create_zd_by_ip_addr(_cfg.pop('zd_ip_addr'))

    return _cfg


def do_test(cfg):    
    return {'create' : _create_user,
            'edit' : _edit_user,
            'clone' : _clone_user,
            'get' : _get_user,
            'get_all' : _get_all_users,
            'delete' : _delete_user,
            'delete_all' : _delete_all_users,}[cfg['action']](cfg)                                                                                                                                                  
 
                                                                                                                                                                                  
def do_clean_up(cfg):
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)

    res = None  
    try:
        res = do_test(tcfg)
    finally:
        do_clean_up(tcfg)
        
    return res['result']


def _is_user_info(k):
    user_info = ['username', 'fullname', 'password', 'confirm_password', 'role', 'number']
    for u in user_info:
        if u == k:
            return True
        
    return False


def _create_user(cfg):  
    user.create_user(cfg['zd'], cfg['user_cfg'])       
    cfg['result'] = 'PASS'
    return cfg


def _edit_user(cfg):
    value = cfg.has_key('user')
    if value:
        user.edit_user(cfg['zd'], cfg['user'], cfg['user_cfg'])
        cfg['result'] = 'PASS'
        return cfg
    
    else:
        raise Exception("Please identify the user you want to edit with argument: user !")


def _clone_user(cfg): 
    value = cfg.has_key('user')
    if value:
        user.clone_user(cfg['zd'], cfg['user'], cfg['user_cfg'])
        cfg['result'] = 'PASS'
        return cfg
    
    else:
        raise Exception("Please identify the user you want to clone with argument: user !")        


def _get_user(cfg):
    value = cfg.has_key('user')
    if value:
        logging.info(user.get_user(cfg['zd'],cfg['user']))
        cfg['result'] = 'PASS'
        return cfg
    
    else:
        raise Exception("Please identify the user you want to get with argument: user !")


def _get_all_users(cfg):
    logging.info(user.get_all_users(cfg['zd']))
    cfg['result'] = 'PASS'
    return cfg


def _delete_user(cfg):
    value = cfg.has_key('user')
    if value:
        user.delete_user(cfg['zd'], cfg['user'])
        cfg['result'] = 'PASS'
        return cfg
    
    else:
        raise Exception("Please identify the user you want to delete with argument: user !")


def _delete_all_users(cfg):
    user.delete_all_users(cfg['zd'])
    cfg['result'] = 'PASS'
    return cfg
