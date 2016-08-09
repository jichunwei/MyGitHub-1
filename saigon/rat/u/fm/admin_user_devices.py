'''
1. Create a user
    + Go to Administer > Users
    + Click on 'Create a user account'
    + Input username, password, user role. Then click ok
    + Ex: tea.py u.fm.admin_user_devices fm_ip_addr=97.74.124.173 fm_verion='9'
          action='create_user' usr_cfg="{'username':'tubn','password':'abc',
                                'confirm_password':'abc','role':'Group Administrator'}"

2. Create a group of devices
    + Go to Administer > Device Assignments
    + Click on 'Create Device Group'
    + Input group name, then click ok.
    + Click on 'Assign Devices' link of group that just created above
    + Select devices that will belong to this group,  then click button 'Add'
    + Ex: tea.py u.fm.admin_user_devices fm_ip_addr=97.74.124.173 fm_verion='9'
          action='create_dv_group' dv_cfg={'groupname':'my_test_device_group',
                                            'matches':[dict(model='zf7942')]}

3. Assign groups to a user
    + Go to Administer > Assign Group Owners
    + Click on 'Assign Group' link of user that we want to assign
    + Select groups that you want assign to this user, then click OK
    + Ex: tea.py u.fm.admin_user_devices fm_ip_addr=97.74.124.173 fm_verion='9'
          action='assign_group_user' group_cfg={'username':'tubn',
                                              'groupnames':['my_test_device_group']}

4. Get list of assigned devices of a group
    + Go to Administer > Device Assignments
    + Click on 'Assign Devices' link of group that you want to get list of devices
    + Get list of devices belong to this group
    + Ex: tea.py u.fm.admin_user_devices fm_ip_addr=97.74.124.173 fm_verion='9'
          action='get_dv_group' dv_cfg={'groupname':'my_test_device_group'}

5. Get list of assigned groups of an user
    + Go to Administer > Assign Group Owners
    + Click on 'Assign Group' link of user that we want to get list of groups
    + Get list of assigned groups belong to this user
    + Ex: tea.py u.fm.admin_user_devices fm_ip_addr=97.74.124.173 fm_verion='9'
          action='get_group_user' group_cfg={'username':'tubn'}


'''


import logging
from pprint import pformat

from RuckusAutoTest.common.utils import dict_by_keys
from RuckusAutoTest.components import create_fm_by_ip_addr, clean_up_rat_env
from RuckusAutoTest.components import Helpers as lib

def create_user(cfg):
    '''
    '''
    config = dict(username='luan', password='abc',
                        confirm_password='abc',
                        role='Network Administrator')
    config.update(cfg['usr_cfg'])
    try:
        lib.fm.user.add(cfg['fm'], cfg['usr_cfg'])
    except Exception, ex:
        return dict(result='FAIL',
                message='Can not create user %s. Error: %s ' % (cfg['usr_cfg'], ex.message))

    return dict(result='PASS',
                message='User %s is created successful' % cfg['usr_cfg'])

def create_device_assignment_group(cfg):
    '''
    '''
    config = {'groupname' : 'my_test_device_group',
              'matches' : [dict(model='zf7942')]}
    config.update(cfg['dv_cfg'])
    try:
        cfg['fm'].lib.da.add(cfg['fm'], config)
    except Exception, ex:
        return dict(result='FAIL',
                message='Can not create group %s. Error: %s' % (cfg['dv_cfg']['groupname'], ex.message))

    return dict(result='PASS',
                message='Group %s is created successful' % cfg['dv_cfg']['groupname'])


def assign_group_to_user(cfg):
    '''
    '''
    config = {'username' : 'my_test_device_group',
              'groupnames' : ['my_test_device_group']}
    config.update(cfg['group_cfg'])
    try:
        cfg['fm'].lib.ga.assign(cfg['fm'], config)
    except Exception, ex:
        return dict(result='FAIL',
                message='Can not assign groups %s to user %s. Error: %s ' % (cfg['group_cfg']['groupnames'],
                                                                    cfg['group_cfg']['username'], ex.message))
    return dict(result='PASS',
                message='Assign groups %s to user %s successful' % (cfg['group_cfg']['groupnames'],
                                                                    cfg['group_cfg']['username']))

def get_list_of_devices_of_group(cfg):
    '''
    '''
    config = {'groupname' : 'my_test_device_group'}

    config.update(cfg['dv_cfg'])
    result = cfg['fm'].lib.da.get_assigned_devices(cfg['fm'], config['groupname'])

    return dict(result='PASS',
                message='List assign groups %s of user %s : %s' % (cfg['group_cfg']['groupnames'],
                                                                   cfg['group_cfg']['username'],
                                                                   result))

def get_list_assign_groups_of_user(cfg):
    '''
    '''
    config = {'username' : 'tubn'}
    config.update(cfg['group_cfg'])

    result = cfg['fm'].lib.ga.get_assigned_groups(cfg['fm'], config['username'])

    return dict(result='PASS',
                message='List assign groups of user %s: %s' % (config['username'], result))


def do_config(cfg):
    p = dict(
        fm_ip_addr = '192.168.30.252',
        fm_version = '9',
        usr_cfg = dict(username='tubn', password='abc',
                       confirm_password='abc',
                       role='Network Administrator'),
        group_cfg = dict(username = 'tubn',
                         groupnames = ['my_test_device_group']),
        dv_cfg = dict(groupname = 'my_test_device_group',
                      matches = [dict(model='zf7942')])
    )
    p.update(cfg)

    p['fm'] = create_fm_by_ip_addr(ip_addr = p.pop('fm_ip_addr'),
                                    version = p.pop('fm_version'))

    return p


def do_test(cfg):

    return {
        'create_user' : create_user,
        'create_dv_group' : create_device_assignment_group,
        'assign_group_user' : assign_group_to_user,
        'get_dv_group' : get_list_of_devices_of_group,
        'get_group_user' : get_list_assign_groups_of_user
    }[cfg['action']](cfg)


def do_clean_up(cfg):
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res
