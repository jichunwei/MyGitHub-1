'''
Created on 2011-1-14
@author: serena.tan@ruckuswireless.com
'''

import re
import logging
from string import Template
from pprint import pformat

from RuckusAutoTest.components.lib.zdcli import get_wlan_group as gwg
from RuckusAutoTest.components.lib.zdcli import get_wlan_info as gwi


CONFIG_WLAN_GROUP_CMD_BLOCK = '''
wlan-group '$wg_name'
'''
SET_NAME= "name '$new_wg_name'\n"
SET_DESCRIPTION= "description '$description'\n"
REMOVE_WLAN_MEMBER= "no wlan '$wlan_name'\n"
ADD_WLAN_MEMBER= "wlan '$wlan_name'\n"
VLAN_OVERRIDE_NONE= "wlan '$wlan_name' vlan override none\n"
VLAN_OVERRIDE_UNTAG= "wlan '$wlan_name' vlan override untag\n"
VLAN_OVERRIDE_TAG= "wlan '$wlan_name' vlan override tag '$tag_override'\n"
SAVE_CONFIG= "exit\n"

DELETE_WLAN_GROUP= "no wlan-group '$wg_name'\n"

ENTRY_NOT_FOUND_MSG = "The entry '$wg_name' could not be found. Please check the spelling, and then try again."
SAVE_SUCCESSFULLY_MSG = "Your changes have been saved."


#--------------------------------------------------------------------------------------------------------------------------
#                                        PUBLIC METHODs 

def configure_wlan_groups(zdcli, wg_cfg_list):
    '''
    Input: a list of wlan group configuration.
    {'wg_name': '',
     'new_wg_name': '',
     'description': '',
     'wlan_member': {
                     'ruckus_1': {},
                     'ruckus_2': {'vlan_override': 'none'},
                     'ruckus_3': {'vlan_override': 'untag'},   
                     'ruckus_4': {'vlan_override': 'tag', 'tag_override': '302'} 
                    }
    }
    ''' 
    fail_name_list = []
    for wg_cfg in wg_cfg_list:
        res = _configure_wlan_group(zdcli, wg_cfg)
        if not res:
            fail_name_list.append(wg_cfg['wg_name'])
    
    if fail_name_list:
        return (False, 'Fail to configure WLAN groups %s in ZD CLI' % fail_name_list)
    
    else:
        return (True, 'Configure all WLAN groups in the cfg list in ZD CLI successfully.')
   
    
def remove_wlan_groups(zdcli, wg_name_list):
    """
    output:
        True: delete wlan groups successfully.
        False: fail to delete wlan groups.
    """
    cmd_block = _construct_remove_wlan_groups_cmd_block(wg_name_list)    
    res = _do_cfg(zdcli, cmd_block)
    if not res:
        return (False, 'Fail to remove WLAN groups %s from ZD CLI' % wg_name_list)
    
    all_wg_name_list = gwg.get_all_wlan_group_name_list(zdcli)
    fail_name_list = []
    for wg_name in wg_name_list:
        if wg_name in all_wg_name_list:
            fail_name_list.append(wg_name)
    
    if fail_name_list:
        return (False, 'Fail to remove WLAN groups %s from ZD CLI' % fail_name_list)
    
    else:
        return (True, 'Remove WLAN groups [%s] from ZD CLI successfully' % wg_name_list)
    
    
def remove_all_wlan_groups(zdcli):
    wg_name_list = gwg.get_all_wlan_group_name_list(zdcli)
    wg_name_list.remove("Default")
    
    if not wg_name_list:
        return (True, "No other WLAN Group except Default.")
    
    return remove_wlan_groups(zdcli, wg_name_list)

 
def remove_wlan_members_from_wlan_group(zdcli, wg_name, wlan_name_list):
    info = gwg.get_wlan_group_by_name(zdcli, wg_name)
    if not info:
        raise (False, "WLAN group [%s] does not exist in ZD CLI" % wg_name)
    
    return _remove_wlan_members_from_wlan_group(zdcli, wg_name, wlan_name_list)


def remove_all_wlan_members_from_wlan_group(zdcli, wg_name):
    wlan_member_list = gwg.get_wlan_member_list(zdcli, wg_name)
    if wlan_member_list == None:
        return (False, 'The WLAN group [%s] does not exist in ZD CLI!' % wg_name)
    
    return _remove_wlan_members_from_wlan_group(zdcli, wg_name, wlan_member_list)


def add_wlan_members_to_wlan_group(zdcli, wg_name, wlan_name_list):
    info = gwg.get_wlan_group_by_name(zdcli, wg_name)
    if not info:
        return (False, "WLAN group [%s] does not exist in ZD CLI" % wg_name)
    
    return _add_wlan_members_to_wlan_group(zdcli, wg_name, wlan_name_list)
    

#--------------------------------------------------------------------------------------------------------------------------
#                                              UN-PUBLIC METHODs 

def _configure_wlan_group(zdcli, conf):   
    '''
    Input: a dict of wlan group configuration.
    {'wg_name': '',
     'new_wg_name': '',
     'description': '',
     'wlan_member': {
                     'ruckus_1': {},
                     'ruckus_2': {'vlan_override': 'none'},
                     'ruckus_3': {'vlan_override': 'untag'},   
                     'ruckus_4': {'vlan_override': 'tag', 'tag_override': '302'} 
                    }
    }
    ''' 
    cfg = {'wg_name': '',
           'new_wg_name': '',
           'description': '',
           'wlan_member': {}
    }
    cfg.update(conf)
    
    info = gwg.get_wlan_group_by_name(zdcli, cfg['wg_name'])
    if info:
        logging.info('Remove all WLAN members from WLAN group [%s] in ZD CLI' % cfg['wg_name'])
        res, msg = remove_all_wlan_members_from_wlan_group(zdcli, cfg['wg_name'])
        if not res:
            logging.info(msg)
            return False
    
    logging.info('Configure WLAN group in ZD CLI with cfg:\n%s' % pformat(cfg, 4, 120))
    cmd_block = _construct_configure_wlan_group_cmd_block(cfg)
    
    res = _do_cfg(zdcli, cmd_block)
    if not res:
        logging.info('Fail to configure WLAN group [%s] in ZD CLI!' % cfg['wg_name'])
        return False
    
    res, msg = _verify_wlan_group_in_cli(zdcli, cfg)
    if res:
        logging.info('Configure WLAN group [%s] in ZD CLI successfully!' % cfg['wg_name'])
        return True
    
    else:
        logging.info('Fail to configure WLAN group [%s] in ZD CLI:\n%s' % (cfg['wg_name'], msg))
        return False
    
    
def _verify_wlan_group_in_cli(zdcli, cfg):
    '''
    Input: a dict of wlan group configuration.
    {'wg_name': '',
     'new_wg_name': '',
     'description': '',
     'wlan_member': {
                     'ruckus_1': {},
                     'ruckus_2': {'vlan_override': 'none'},
                     'ruckus_3': {'vlan_override': 'untag'},   
                     'ruckus_4': {'vlan_override': 'tag', 'tag_override': '302'} 
                    }
    }
    ''' 
    new_wg_name = cfg.pop('new_wg_name')
    if new_wg_name:
        cfg['wg_name'] = new_wg_name
        
    cli_info = gwg.get_wlan_group_by_name(zdcli, cfg['wg_name'])
    
    _cli_info = _format_cli_info(cli_info)
    expect_info = _define_expect_info(cfg)
    res, msg = _expect_info_is_in_cli(_cli_info, expect_info)
    if res:
        return (True, msg)
    
    else:
        return (False, msg)      
    
    
def _add_wlan_members_to_wlan_group(zdcli, wg_name, wlan_name_list):
    cmd_block = _construct_add_wlan_members_cmd_block(wg_name, wlan_name_list)    
    res = _do_cfg(zdcli, cmd_block)
    if not res:
        return (False, 'Fail to configure WLAN group [%s] in ZD CLI' % wg_name)
    
    wlan_member_list = gwg.get_wlan_member_list(zdcli, wg_name)
    fail_name_list = []
    for wlan_name in wlan_name_list:
        if wlan_name not in wlan_member_list:
            fail_name_list.append(wlan_name)
            wlan_info = gwi.get_wlan_by_ssid(zdcli, wlan_name)
            if not wlan_info:
                logging.info('WLAN [%s] does not exist in ZD CLI.' % wlan_name)
    
    if fail_name_list:
        return (False, 'Fail to add WLANs %s to WLAN group [%s] in ZD CLI' % (fail_name_list, wg_name))
    
    else:
        return (True, 'Add WLANs %s to WLAN group [%s] in ZD CLI successfully' % (wlan_name_list, wg_name))


def _construct_add_wlan_members_cmd_block(wg_name, wlan_name_list):
    cmd_block = Template(CONFIG_WLAN_GROUP_CMD_BLOCK).substitute(dict(wg_name = wg_name))
    for wlan_name in wlan_name_list:
        cmd_block = cmd_block + Template(ADD_WLAN_MEMBER).substitute(dict(wlan_name = wlan_name))
        
    cmd_block = cmd_block + SAVE_CONFIG
    
    return cmd_block

    
def _remove_wlan_members_from_wlan_group(zdcli, wg_name, wlan_name_list):
    cmd_block = _construct_remove_wlan_members_cmd_block(wg_name, wlan_name_list)    
    res = _do_cfg(zdcli, cmd_block)
    if not res:
        return (False, 'Fail to configure WLAN group [%s] in ZD CLI' % wg_name)
    
    wlan_member_list = gwg.get_wlan_member_list(zdcli, wg_name)
    if wlan_member_list == None:
        return (False, 'The WLAN group [%s] does not exist in ZD CLI!' % wg_name)
    
    fail_name_list = []
    for wlan_name in wlan_name_list:
        if wlan_name in wlan_member_list:
            fail_name_list.append(wlan_name)
    
    if fail_name_list:
        return (False, 'Fail to remove WLANs %s from WLAN group [%s] in ZD CLI' % (fail_name_list, wg_name))
    
    else:
        return (True, 'Remove WLANs %s from WLAN group [%s] in ZD CLI successfully' % (wlan_name_list, wg_name))
    
    
def _construct_remove_wlan_members_cmd_block(wg_name, wlan_name_list):
    cmd_block = Template(CONFIG_WLAN_GROUP_CMD_BLOCK).substitute(dict(wg_name = wg_name))
    for wlan_name in wlan_name_list:
        cmd_block = cmd_block + Template(REMOVE_WLAN_MEMBER).substitute(dict(wlan_name = wlan_name))
        
    cmd_block = cmd_block + SAVE_CONFIG
    
    return cmd_block


def _construct_remove_wlan_groups_cmd_block(wg_name_list):
    cmd_block = '''
    '''
    for name in wg_name_list:
        cmd_block = cmd_block + Template(DELETE_WLAN_GROUP).substitute(dict(wg_name = name))
        
    cmd_block = cmd_block + SAVE_CONFIG
    
    return cmd_block


def _do_cfg(zdcli, cmd_block):
    if 'exit' not in cmd_block:
        cmd_block = cmd_block + SAVE_CONFIG
        
    logging.info('Do configuration with cmd_block:\n%s' % cmd_block)
    res = zdcli.do_cfg(cmd_block)
    logging.info('cmd_block execution result:\n%s' % pformat(res, 4, 120))
    if SAVE_SUCCESSFULLY_MSG not in res['exit'][0]:
        zdcli.back_to_priv_exec_mode(back_cmd = 'quit', print_out = True)
        return False
    
    return True


def _expect_info_is_in_cli(cli_dict, expect_dict):
    expect_ks = expect_dict.keys()
    cli_ks = cli_dict.keys()
    for k in expect_ks:
        if k not in cli_ks:
            return (False, 'The parameter [%s, %s] in expect_dict does not exist in ZD CLI' % (k, expect_dict))
        
        if type(expect_dict[k]) is dict:
            res, msg = _expect_info_is_in_cli(cli_dict[k], expect_dict[k])
            if not res:
                return (False, msg)
        
        elif cli_dict[k] != expect_dict[k]:
            rule1 = '^' + expect_dict[k] + '.*'
            rule2 = '.*' + expect_dict[k] + '$'
            re_rule1 = re.compile(rule1)
            re_rule2 = re.compile(rule2)
            if (not re_rule1.search(cli_dict[k])) or (not re_rule2.search(cli_dict[k])):
                return (False, 'The value of parameter [%s] in expect_dict is [%s] not the same as in ZD CLI [%s]' % (k, expect_dict[k], cli_dict[k]))         

    return (True, '')


def _construct_configure_wlan_group_cmd_block(cfg): 
    '''
    Input: a dict of wlan group configuration.
    {'wg_name': '',
     'new_wg_name': '',
     'description': '',
     'wlan_member': {
                     'ruckus_1': {},
                     'ruckus_2': {'vlan_override': 'none'},
                     'ruckus_3': {'vlan_override': 'untag'},   
                     'ruckus_4': {'vlan_override': 'tag', 'tag_override': '302'} 
                    }
    }
    '''
    cmd_block = Template(CONFIG_WLAN_GROUP_CMD_BLOCK).substitute(dict(wg_name = cfg['wg_name']))
    
    if cfg['new_wg_name']:
        cmd_block = cmd_block + Template(SET_NAME).substitute(dict(new_wg_name = cfg['new_wg_name']))
    
    if cfg['description'] and cfg['wg_name'] != "Default":
        cmd_block = cmd_block + Template(SET_DESCRIPTION).substitute(dict(description = cfg['description']))

    if cfg['wlan_member']:
        wlans = cfg['wlan_member'].keys()
        for wlan in wlans:
            vlan_override = cfg['wlan_member'][wlan].get('vlan_override')
            if not vlan_override:
                cmd_block = cmd_block + Template(ADD_WLAN_MEMBER).substitute(dict(wlan_name = wlan))
                
            elif vlan_override == 'none':
                cmd_block = cmd_block + Template(VLAN_OVERRIDE_NONE).substitute(dict(wlan_name = wlan))
            
            elif vlan_override == 'untag':
                #Behavior Change after 9.3
                cmd_block = cmd_block + Template(VLAN_OVERRIDE_NONE).substitute(dict(wlan_name = wlan))
                #cmd_block = cmd_block + Template(VLAN_OVERRIDE_UNTAG).substitute(dict(wlan_name = wlan))
            
            elif vlan_override == 'tag':
                tag_override = cfg['wlan_member'][wlan].get('tag_override')
                cmd_block = cmd_block + Template(VLAN_OVERRIDE_TAG).substitute(dict(wlan_name = wlan, tag_override = tag_override))
            
            else:
                raise Exception("Unexpect vlan override settings")
                
    cmd_block = cmd_block + SAVE_CONFIG
    
    return cmd_block     
                                                          

def _define_expect_info(cfg):
    '''
    Input:
    {'wg_name': '',
     'description': '',
     'wlan_member': {'ruckus_1': {},
                     'ruckus_2': {'vlan_override': 'none'},
                     'ruckus_3': {'vlan_override': 'untag'},   
                     'ruckus_4': {'vlan_override': 'tag', 'tag_override': '302'} 
                    }
    }
    Output:
    {'Name': '',
     'Description': '',
     'WLAN Service': {'ruckus_1': {'VLAN': ''},
                      'ruckus_2': {'VLAN': ''},
                      'ruckus_3': {'VLAN': '1(Untag)'},
                      'ruckus_4': {'VLAN': '302(Tag)'}}}
    '''
    info = dict()
    info['Name'] = cfg['wg_name']
    if cfg['description']:
        info['Description'] = cfg['description']
        
    if cfg['wlan_member']:
        wlan_service = {}
        wlans = cfg['wlan_member'].keys()
        for wlan in wlans:
            wlan_service[wlan] = {}
            vlan_override = cfg['wlan_member'][wlan].get('vlan_override')
            if not vlan_override or vlan_override == 'none':
                wlan_service[wlan]['VLAN'] = ''
                
            elif cfg['wlan_member'][wlan]['vlan_override'] == 'untag':
                wlan_service[wlan]['VLAN'] = ''#Behavior Change after 9.3
                #wlan_service[wlan]['VLAN'] = '1(Untag)'
                
            elif cfg['wlan_member'][wlan]['vlan_override'] == 'tag':
                wlan_service[wlan]['VLAN'] = '%s' % cfg['wlan_member'][wlan]['tag_override']
        
        info['WLAN Service'] = wlan_service
    
    return info


def _format_cli_info(info):
    '''
    Input:
    {'Name': '',
     'Description': '',
     'VLAN Override': {'Status': 'Enabled'},
     'WLAN Service': {'WLAN1': {'NAME': 'ruckus_1', 'VLAN': ''},
                      'WLAN2': {'NAME': 'ruckus_2', 'VLAN': '1(Untag)'},
                      'WLAN3': {'NAME': 'ruckus_3', 'VLAN': '302(Tag)'}}}
    }
    Output:
    {'Name': '',
     'Description': '',
     'VLAN Override': {'Status': 'Enabled'}
     'WLAN Service': {'ruckus_1': {'VLAN': ''},
                      'ruckus_2': {'VLAN': '1'},
                      'ruckus_3': {'VLAN': '302'}}}
    '''       
    if info.has_key('WLAN Service'):
        wlan_members = {}
        wlans = info['WLAN Service'].keys()
        for wlan in wlans:  
            wlan_name = info['WLAN Service'][wlan].pop('NAME')
            wlan_members[wlan_name] = info['WLAN Service'][wlan]
            
        info['WLAN Service'] = wlan_members

    return info
            
                
