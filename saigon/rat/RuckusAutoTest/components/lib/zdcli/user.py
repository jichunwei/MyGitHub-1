'''
Created on 2010-11-4
@author: serena.tan@ruckuswireless.com
'''


import logging
from string import Template
from pprint import pformat

from RuckusAutoTest.components.lib.zdcli import output_as_dict


# Command templates
GET_USER_ALL= "show user all"
GET_USER_BY_NAME= "show user name '$name'"

SET_USER_NAME="user-name '$name'\n"
SET_USER_FULLNAME= "full-name '$fullname'\n"
SET_USER_ROLE= "role '$role'\n"
SET_USER_PASSWORD= "password '$password'\n"
SAVE_USER_CONFIG= "exit\n"
CONFIG_USER_CMD_BLOCK = '''
user '$user'
'''

DELETE_USER= "no user '$name'"

ENTRY_NOT_FOUND_MSG = "The entry '$name' could not be found. Please check the spelling, and then try again."

KEY_CONST={'name':'User Name'
           }

#--------------------------------------------------------------------------------------------------------------------------
#                                              PUBLIC METHODs 

def get_user_by_name(zdcli, name):
    """
    Output:
            a dictionary of the user information:
            {
             'User Name':
             'Full Name':
             'Password': 
             'Role':
            }
            None: the user does not exist.
            exception
    """
    cmd = Template(GET_USER_BY_NAME).substitute(dict(name = name))
    entry_not_found_msg = Template(ENTRY_NOT_FOUND_MSG).substitute(dict(name = name))
    
    logging.info('Get the information of user [%s] from ZD CLI by command [%s].' % (name, cmd))
    try:
        info = _get_user_info(zdcli, cmd)
        
    except Exception, ex:
        if entry_not_found_msg in ex.message:
            logging.info('The user [%s] does not exist in ZD CLI!' % name)
            return None
        
        else:
            raise Exception(ex.message)
    
    user = info.values()[0]
    logging.info('The information of user [%s] in ZD CLI is:\n%s.' % (name, pformat(user, 4, 120)))

    return user


def get_user_all(zdcli):
    """
    Output:
            a dictionary of all users information:
            {
             '1': {
                   'User Name':
                   'Full Name':
                   'Password': 
                   'Role':
                  },
             ...
            }
            {} : no user exists.
            exception
    """
    logging.info('Get all users information via ZD CLI by command [%s].' % GET_USER_ALL)
    user_all = _get_user_info(zdcli, GET_USER_ALL)
    
    logging.info("The information of all users in ZD CLI is:\n%s." % pformat(user_all, 4, 120))
    
    return user_all


def get_user_name_list(zdcli):
    """
    Output:
            name_list: a list of all user's name.
    """
    name_list = []
    
    info_dict = get_user_all(zdcli)
    keys = info_dict.keys()
    for k in keys:
        name = info_dict[k]['User Name']
        name_list.append(name)
    
    return name_list


def create_user(zdcli, name, fullname='', role='', password='', number=1):
    """
    output:
        True: create user successfully.
        False: fail to create user.
    """   
    if number > 1:
        for i in range(number):
            name_t = '%s_%d' % (name, i)
            res = _create_user(zdcli, name_t, fullname, role, password)
            if not res:
                return False
        return True
    
    else:
        return _create_user(zdcli, name, fullname, role, password)
    
    
def edit_user(zdcli, user, name='', fullname='', role='', password=''):
    """
    output:
        True: edit user successfully.
        False: fail to edit user.
    """
    info = get_user_by_name(zdcli, user)
    if not info:
        return False
    
    value = _set_user(zdcli, user, name, fullname, role, password)
    if not value:
        logging.info('Fail to edit user [%s] in ZD CLI!' % user)
        return False
    
    if name != '':
        res = _verify_user_in_cli(zdcli, name, fullname, role, '******', type = 'edit')
    
    else:
        res = _verify_user_in_cli(zdcli, user, fullname, role, '******', type = 'edit')
        
    if res:
        logging.info('Edit user [%s] in ZD CLI successfully!' % user)
        return True
    
    else:
        logging.info('Fail to edit user [%s] in ZD CLI!' % user)
        return False


def delete_user(zdcli, name):
    """
    output:
          exception: fail to edit user.
    """
    info = get_user_by_name(zdcli, name)
    if not info:
        return
    
    cmd = Template(DELETE_USER).substitute(dict(name = name))
    
    logging.info('Delete user [%s] by command [%s].' % (name, cmd))
    res = zdcli.do_cfg(cmd)
    logging.info('cmd execution result:\n%s' % res)
    
    info = get_user_by_name(zdcli, name)
    if info:
        raise Exception('Fail to delete user [%s]!' % name)
    
    else:
        logging.info('Delete user [%s] successfully!' % name)


def delete_all_users(zdcli):
    users = get_user_all(zdcli)
    name_list = [user[KEY_CONST['name']] for id, user in users.items()]
    for name in name_list:
        delete_user(zdcli, name)
    

def verify_all_user_by_gui(cli_info_dict, gui_info_list):
    """
    This method is used to verify whether the information of all users shown in ZD CLI is the same as in ZD GUI.
    Input:
        cli_info_dict:
            {
             '1': {
                   'User Name':
                   'Full Name':
                   'Password': 
                   'Role':
                  },
             ...
            }
        gui_info_list:
            [
             {
              'username':
              'fullname': 
              'role':
             },
             ...
            ]
    Output:
        True: The information of all users shown in ZD CLI is the same as in ZD GUI
        False: The information of all users in ZD CLI is not the same as in ZD GUI
    """
    logging.info('Verify all users information shown in ZD CLI with ZD GUI.')
    
    cli_info_list =  cli_info_dict.values()
    
    cli_len = len(cli_info_list)
    gui_len = len(gui_info_list)

    if cli_len != gui_len:
        logging.info('The number of users in ZD CLI [%s] is not the same as in ZD GUI [%s]' % (cli_len, gui_len))
        return False
    
    if cli_len == 0:
        logging.info('No user exists in ZD CLI and ZD GUI!')
        return True
    
    for i in range(cli_len):
        for j in range(gui_len):
            if cli_info_list[i]['User Name'] == gui_info_list[j]['username']:
                res = _verify_user_by_gui(cli_info_list[i], gui_info_list[j])
                if not res:
                    return False
                
                else:
                    break
                
            if j == gui_len - 1:
                logging.info('The user [%s] exists in ZD CLI, but not in ZD GUI' % cli_info_list[i]['User Name'])
                return False
            
    logging.info('The information of all users shown in ZD CLI is the same as in ZD GUI')
    return True
    

def verify_user_by_gui(cli_dict, gui_dict):
    """
    This method is used to verify whether the information of a user shown in ZD CLI is the same as in ZD GUI.
    Input:
        cli_user:
            {
                 'User Name':
                 'Full Name':
                 'Password': 
                 'Role':
            }
        gui_user:
            {
                'username': 
                'fullname': 
                'role': 
            }
    Output:
        True: The user information shown in ZD CLI is the same as in ZD GUI
        False: The user information shown in ZD CLI is not the same as in ZD GUI
    """
    logging.info('Verify the user information shown in ZD CLI with ZD GUI.')
    
    if cli_dict == None:
        if gui_dict == None:
            logging.info('No user exists in ZD CLI or ZD GUI!')
            return True
        
        else:
            logging.info('The user [%s] exists in ZD GUI but not in ZD CLI!' % gui_dict['username'])
            return False
        
    else:
        if gui_dict == None:
            logging.info('The user [%s] exists in ZD CLI but not in ZD GUI!' % cli_dict['User Name'])
            return False
        
    res = _verify_user_by_gui(cli_dict, gui_dict)
    if res:
        logging.info('The information of user [%s] shown in ZD CLI is the same as in ZD GUI!' % cli_dict['User Name'])
        return True
    
    else:
        logging.info('The information of user [%s] shown in ZD CLI is not the same as in ZD GUI!' % cli_dict['User Name'])
        return False


def verify_user_cfg_in_gui(cli_cfg_dict, gui_info_dict):
    '''
    Input:
        cli_cfg_dict: a dict of configuration used to configure a user in  ZD CLI.
        {'user': name of the user to be edited, don't need this parameter when create a new user. 
         'name': name of the user when create a new user, new name of the user when edit a existing user.  
         'fullname': '', 
         'role': '', 
         'password': ''
        }
        gui_info_dict: a dict of user information shown in ZD GUI.
        {'username': '',
         'fullname': '',
         'role': ''
        }
    '''
    expect_gui_info = _define_expect_gui_info(cli_cfg_dict)

    if gui_info_dict == None:
        return (False, 'Not find the user [%s] in ZD GUI' % expect_gui_info['username'])
    
    res, msg = _expect_is_in_dict(expect_gui_info, gui_info_dict)
    if res:
        return (True, 'The user configuration is correct in ZD GUI')
    
    else:
        return (False, msg)
    
    
#--------------------------------------------------------------------------------------------------------------------------
#                                              UN-PUBLIC METHODs 

def _get_user_info(zdcli, cmd):
    data = zdcli.do_show(cmd)
    if not data.startswith("User:"):
        raise Exception(data)
                        
    info = output_as_dict.parse(data)
    if not info:
        return info

    else:
        return info['User']['ID']


def _create_user(zdcli, name, fullname='', role='', password=''):
    value = _set_user(zdcli, user = name, fullname = fullname, role = role, password = password)
    if not value:
        logging.info('Fail to create user [%s] in ZD CLI!' % name)
        return False
    
    res = _verify_user_in_cli(zdcli, name, fullname, role)
    if res:
        logging.info('Create user [%s] in ZD CLI successfully!' % name)
        return True
    
    else:
        logging.info('Fail to create user [%s] in ZD CLI!' % name)
        return False
    
    
def _set_user(zdcli, user, name='', fullname='', role='', password=''):   
    cmd_block = _construct_cmd_block(user, name, fullname, role, password)
    logging.info('Set user [%s] with cmd_block:\n%s' % (user, cmd_block))
    
    res = zdcli.do_cfg(cmd_block, raw = True)
    logging.info('cmd_block execution result:\n%s' % pformat(res, 4, 120))
    
    if "The operation doesn't execute successfully." in res['exit'][0]:
        zdcli.back_to_priv_exec_mode(back_cmd = 'quit', print_out = True)
        return False
    
    return True
        
        
def _construct_cmd_block(user, name='', fullname='', role='', password=''):
    if user != '':
        cmd_block = Template(CONFIG_USER_CMD_BLOCK).substitute(dict(user = user))
        
    if name != '':
        name_cmd = Template(SET_USER_NAME).substitute(dict(name = name))
        cmd_block = cmd_block + name_cmd
        
    if fullname != '':
        fullname_cmd = Template(SET_USER_FULLNAME).substitute(dict(fullname = fullname))
        cmd_block = cmd_block + fullname_cmd
        
    if role !='':
        role_cmd = Template(SET_USER_ROLE).substitute(dict(role = role))
        cmd_block = cmd_block + role_cmd
    
    if password != '':
        password_cmd = Template(SET_USER_PASSWORD).substitute(dict(password = password))
        cmd_block = cmd_block + password_cmd
    
    cmd_block = cmd_block + SAVE_USER_CONFIG
    
    return cmd_block    


def _verify_user_in_cli(zdcli, name, fullname='', role='', password='******', type='create'):
    info = get_user_by_name(zdcli, name)
    if info == None:
        return False
    
    expect_info = _define_expect_info(name, fullname, role, password, type)

    cfg_ks = expect_info.keys()
    info_ks = info.keys()
    for k in cfg_ks:
        ##zj 2014-0211 fix ZF-7411
        if k.lower()=='password' :
            continue
        ####zj 2014-0211 fix ZF-7411
        if k not in info_ks or expect_info[k] != info[k]:
            logging.info('The parameter [%s] of user [%s] does not configure successfully in ZD CLI' % (k, name))
            return False
    
    return True

        
def _define_expect_info(name, fullname='', role='', password='******', type='create'):
    '''
    format the user cfg to a dictionary as below:
        {
         'User Name':
         'Full Name':
         'Password': 
         'Role':
        }
    '''
    info = dict()
    info['User Name'] = str(name)
    
    if type == 'create':
        info['Full Name'] = str(fullname)
        info['Password'] = str(password)
        if role != '':
            info['Role'] = str(role)
            
        else:
            info['Role'] = 'Default'
            
    elif type == 'edit':
        if fullname != '':
            info['Full Name'] = str(fullname)
        
        if password != '':
            info['Password'] = str(password)
            
        if role != '':
            info['Role'] = str(role)

    return info
    

def _verify_user_by_gui(cli_user, gui_user):
    _gui_user = _format_gui_info(gui_user)
    
    keys = _gui_user.keys()
    for k in keys:
        if not cli_user.has_key(k):
            logging.info("The parameter [%s] is not showed in ZD CLI!" % k)
            return False
        
        elif cli_user[k] != _gui_user[k]:
            logging.info("The information in ZD GUI [%s = %s] is not the same as in ZD CLI [%s =%s]" % (k, _gui_user[k], k, cli_user[k]))
            return False
    
    return True


def _format_gui_info(gui_user):
    """
    format the user information got from ZD GUI to the format in ZD CLI.
    Input:
        gui_user:
            {
             'username': 
             'fullname': 
             'role': 
            }
    Output:
            {
             'User Name':
             'Full Name':
             'Role':
            }
    """
    _info = dict()
    
    if gui_user.has_key('username'):
        _info['User Name'] = gui_user['username']
    
    if gui_user.has_key('fullname'):
        _info['Full Name'] = gui_user['fullname']
    
    if gui_user.has_key('role'):
        _info['Role'] = gui_user['role']

    return _info


def _define_expect_gui_info(cli_cfg_dict):
    '''
    Input:
        cli_cfg_dict: a dict of configuration used to configure a user in  ZD CLI.
        {'user': name of the user to be edited, don't need this parameter when create a new user. 
         'name': name of the user when create a new user, new name of the user when edit a existing user.  
         'fullname': '', 
         'role': '', 
         'password': ''
        }
    Output:
        expect_gui_info:
        {'username': '',
         'fullname': '',
         'role': ''
        }
    '''
    expect_gui_info = dict()
    if cli_cfg_dict.get('user'):
        if cli_cfg_dict.get('name'):
            expect_gui_info['username'] = cli_cfg_dict['name']
        
        else:
            expect_gui_info['username'] = cli_cfg_dict['user']
    
    else:
        expect_gui_info['username'] = cli_cfg_dict['name']
        
    if cli_cfg_dict.get('fullname'):
        expect_gui_info['fullname'] = cli_cfg_dict['fullname']
        
    if cli_cfg_dict.get('role'):
        expect_gui_info['role'] = cli_cfg_dict['role']
    
    return expect_gui_info


def _expect_is_in_dict(expect_dict, original_dict):
    expect_ks = expect_dict.keys()
    orignal_ks = original_dict.keys()
    for k in expect_ks:
        if k not in orignal_ks:
            return (False, 'The parameter [%s] does not exist in dict: %s' % (k, original_dict))
        
        if type(expect_dict[k]) is dict:
            res, msg = _expect_is_in_dict(expect_dict[k], original_dict[k])
            if not res:
                return (False, msg)
        
        elif original_dict[k] != expect_dict[k]:
            return (False, 'The value [%s] of parameter [%s] is not correct in dict: %s ' % (expect_dict[k], k, original_dict))         

    return (True, '')
