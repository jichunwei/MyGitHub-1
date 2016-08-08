'''
Author#Jane(guo.can@odc-ruckuswireless.com)
date#2013-7-11
This file is used for white list create/delete/add rule/del rule etc.
'''

import logging
import re
import time
import os
from string import Template

from RuckusAutoTest.components.lib.zdcli import output_as_dict

CREATE_WHITE_LIST = """whitelist '$name'\n"""

DELETE_WHITE_LIST = """no whitelist '$name'\n"""

EDIT_RULE ="""rule '$idx'\n"""

DELETE_RULE ="""no rule '$idx'\n"""

EDIT_MAC_ADDR = """mac '$mac'\n"""

EDIT_IP_ADDR = """ip '$ip'\n"""

EDIT_RULE_DESCRIPTION = """description '$description'\n"""

EDIT_NAME = """name '$name'\n"""

EDIT_DESCRIPTION = """description '$description'\n"""

SAVE_SERVER_CONFIG = "exit\n"

SAVE_SERVER_CONFIG_NO_CHECK = "end\n"

SAVE_SERVER_CONFIG_QUIT = "quit\n"

SHOW_WHITELIST_ALL= "show whitelist\n"

SHOW_WHITELIST_ONE= "whitelist '$name'\nshow\n"

TIME_OUT = 40

def _do_excute_cmd(zdcli, cmd, expect_failed = False, timeout = "", check_dict = ""):
    """
    check output value
    support negative test, default is disable
    """
    try:
        logging.info("CLI command is: %s" % cmd)
        if not timeout:
            global TIME_OUT
            timeout = TIME_OUT
        #Don't exit to cfg in this function,so parent function need add exit comman itself.
        res = zdcli.do_cfg(cmd, timeout = timeout, raw = True, exit_to_cfg = False)
        time.sleep(2)
        
        #if have check dict, check the command and value
        if check_dict:
            err_list = []
            for check_cmd in check_dict:
                if res.has_key(check_cmd):
                    if check_dict[check_cmd] in res[check_cmd][0]:
                        logging.info('Command return check success')
                    else:
                        logging.info('Command return check fail, return is %s, expect is %s' % (res[check_cmd], check_dict[check_cmd][0]))
                        err_list.append(check_cmd)
                else:
                    logging.info("Can't find this command")
                    return False
            
            if err_list:
                logging.info('Check failed-wrong behavior')
                return False
            else:
                logging.info('Check success-correct behavior')                           
                        
        if res.has_key('exit'):
            if "Your changes have been saved." not in res['exit'][0]:
                if expect_failed:
                    zdcli.back_to_priv_exec_mode(back_cmd = 'quit', print_out = True)
                    logging.info('Configure failed-correct behavior')
                    return True
                else:
                    zdcli.back_to_priv_exec_mode(back_cmd = 'quit', print_out = True)
                    logging.info('Configure failed-wrong behavior. Result is %s' % res)
                    return False
        
        logging.info('Configure success')
        return True          
    except Exception, ex:
        errmsg = ex.message
        raise Exception(errmsg)

def _edit_white_list(zdcli, white_list_name, whitelist_conf = {}, expect_failed = False, timeout = ""):
    '''
    whitelist_conf = {'name':'',
                      'description':''
                     }
    '''
    logging.info('Edit white list [%s]' % white_list_name)
    cmd = Template(CREATE_WHITE_LIST).substitute(dict(name = white_list_name))
    
    new_name = whitelist_conf.get('name')
    if new_name:
        cmd += Template(EDIT_NAME).substitute(dict(name = new_name))
    
    description = whitelist_conf.get('description')
    if description:
        cmd += Template(EDIT_DESCRIPTION).substitute(dict(description = description))
        
    cmd += SAVE_SERVER_CONFIG
    return _do_excute_cmd(zdcli, cmd, expect_failed, timeout)
    
def _edit_rule(zdcli, white_list_name, rule_conf, expect_failed = False, timeout = ""):
    '''
    rule_conf = {'1':{
                        'mac':'aa:bb:11:22:33:44',
                        'ip':'192.168.0.6',
                        'description':'gateway'
                      },
                '2':{
                        'mac':'aa:bb:11:22:33:44'
                    }
                }
    '''
    rule_list = []
    for idx in rule_conf:
        rule_list.append(int(idx))
        
    rule_list.sort()
    
    cmd = Template(CREATE_WHITE_LIST).substitute(dict(name = white_list_name))
    
    for idx in rule_list:
        logging.info('Edit rule [%s] for white list [%s]' % (idx, white_list_name))
        rule_cmd = Template(EDIT_RULE).substitute(dict(idx = str(idx)))
        mac = rule_conf[str(idx)].get('mac')
        if mac:
            rule_cmd+= Template(EDIT_MAC_ADDR).substitute(dict(mac = mac))
            
        ip = rule_conf[str(idx)].get('ip')
        if ip:
            rule_cmd+= Template(EDIT_IP_ADDR).substitute(dict(ip = ip))

        description = rule_conf[str(idx)].get('description')
        if description:
            rule_cmd+= Template(EDIT_RULE_DESCRIPTION).substitute(dict(description = description))
                    
        rule_cmd +=SAVE_SERVER_CONFIG_NO_CHECK
        
        cmd += rule_cmd
        
    cmd += SAVE_SERVER_CONFIG
    return _do_excute_cmd(zdcli, cmd, expect_failed, timeout)

def _show_white_list(zdcli, timeout = ""):
    """
    ruckus(config)#show whitelist
    White Lists:
      ID:
        1:
          Name= test1
          Description= test1
          Rules:
            1:
              Description=
              MAC = 
              IP Address = 192.168.0.252
    """
    data = zdcli.do_show(SHOW_WHITELIST_ALL, True, False, timeout)
    if type(data) is list:
        data = data[0]
    if not data.startswith("White Lists:"):
        raise Exception(data)
                        
    info = output_as_dict.parse(data)
    if not info or not info['White Lists'].get('ID'):
        return None
    else:
        logging.info('Show white list info: [%s]' % info['White Lists']['ID'])
        return info['White Lists']['ID']

def _show_special_white_list(zdcli, whitelist_name, timeout = ""):
    """
    ruckus(config)# whitelist 222
    The White List entry has been loaded successfully.
    ruckus(config-whitelist)# show
    White Lists:
      ID:
        2:
          Name= 222
          Description=
          Rules:
            1:
              Description=
              MAC = 12:11:11:11:11:11
              IP Address =
    """
    if not timeout:
        global TIME_OUT
        timeout = TIME_OUT
    cmd = Template(SHOW_WHITELIST_ONE).substitute(dict(name = whitelist_name))
    cmd += SAVE_SERVER_CONFIG_QUIT
    data = zdcli.do_cfg(cmd, raw = True, exit_to_cfg = False, timeout = timeout)
    info_all = data['show'][0]
    info = output_as_dict.parse(info_all)
    
    if not info:
        return None
    else:
        logging.info('Show white list info: [%s]' % info['White Lists']['ID'])
        return info['White Lists']['ID']

def _delete_rule(zdcli, white_list_name, rule_conf, expect_failed = False, timeout = ""):
    '''
    rule_conf = {'1':{
                        'mac':'aa:bb:11:22:33:44',
                        'ip':'192.168.0.6'
                      },
                '2':{
                        'mac':'aa:bb:11:22:33:44'
                    }
                }
    '''
    #Get rule list and sort, delete from the last one to the first one
    rule_list = []
    for idx in rule_conf:
        rule_list.append(int(idx))
        
    rule_list.sort(reverse = True)
    
    cmd = Template(CREATE_WHITE_LIST).substitute(dict(name = white_list_name))
    for idx in rule_list:
        logging.info('Delete rule [%s] for white list [%s]' % (idx, white_list_name))
        cmd += Template(DELETE_RULE).substitute(dict(idx = str(idx)))
    
    cmd += SAVE_SERVER_CONFIG
    return _do_excute_cmd(zdcli, cmd, expect_failed, timeout)

def create_white_list(zdcli,white_list_name,whitelist_conf = {},expect_failed = False, timeout = ""):
    return _edit_white_list(zdcli, white_list_name, whitelist_conf = {}, expect_failed = False, timeout = "")
    
def delete_white_list(zdcli,white_list_name,expect_failed = False, timeout = "", check_dict=""):
    cmd = Template(DELETE_WHITE_LIST).substitute(dict(name = white_list_name))
    logging.info('Delete white list [%s]' % white_list_name)
    return _do_excute_cmd(zdcli, cmd, expect_failed, timeout, check_dict)

def add_rule(zdcli, white_list_name, rule_conf, expect_failed = False, timeout = ""):
    return _edit_rule(zdcli, white_list_name, rule_conf, expect_failed, timeout)

def delete_rule(zdcli, white_list_name, rule_conf, expect_failed = False, timeout = ""):
    return _delete_rule(zdcli, white_list_name, rule_conf, expect_failed, timeout)

def show_white_list(zdcli, timeout = ""):
    return _show_white_list(zdcli, timeout)

def show_special_white_list(zdcli, whitelist_name, timeout = ""):
    return _show_special_white_list(zdcli, whitelist_name, timeout)

def verify_white_list(zdcli, white_list_name, rule_conf, timeout = ""):
    """
    Show white list info: 
    {'1': 
      {'Rules': 
        {'1': 
            {'IP Address': '192.168.0.250', 'MAC': '', 'Description': ''}, 
        '2': 
            {'IP Address': '192.156.0.5', 'MAC': '', 'Description': ''}
        }, 
      'Name': 'test1', 
      'Description':'test1'
    }, 
    """
    white_lists = _show_special_white_list(zdcli, white_list_name, timeout)  
    if not white_lists:
        logging.info("Can't find white lists.")
        return False
    
    name_flag = False
    for idx in white_lists:
        white_list_one = white_lists[idx]
        if not white_list_one.get('Rules'):
            logging.error("Get white list %s info fail."%(white_list_name))
            return False
        
        if white_list_one['Name'] == white_list_name:
            name_flag = True
            rule_list = white_list_one['Rules']
            
            res = _verify_rule_between_set_get(zdcli, rule_conf, rule_list)
            if not res:
                logging.error("Check white list %s fail."%(white_list_name))  
                return False
    
    if name_flag:
        logging.info("Check white list successful.")        
        return True
    else:
        logging.info("Can't find white list %s" % white_list_name)        
        return False       

def _verify_rule_between_set_get(zdcli, set_conf, get_conf):
    for check_rule in set_conf:
        if type(check_rule) == int:
            check_rule = str(check_rule)
            
        if get_conf.get(check_rule):
            rule = {}
            rule['mac'] = get_conf[check_rule]['MAC']
            rule['ip'] = get_conf[check_rule]['IP Address']
            rule['description'] = get_conf[check_rule]['Description']
            
            check_rule_info = set_conf[check_rule]
            
            for check_key in check_rule_info:
                key = check_rule_info[check_key]
                if not key.lower() == rule[check_key].lower():
                    logging.error("%s is different, set is %s, get is %s" % (check_key, key.lower(),rule[check_key].lower()))
                    return False
        else:
            logging.error("Can't find rule %s in %s " % (check_rule, get_conf))
            return False
          
    logging.info("Check rule successful.")
    return True         

def get_all_white_list(zdcli,timeout = ""):
    all_info =  _show_white_list(zdcli, timeout)
    if not all_info:
        return None
    
    white_lists = []
    for idx in all_info:
        white_list_one = all_info[idx]
        white_lists.append(white_list_one['Name'])
        
    return white_lists