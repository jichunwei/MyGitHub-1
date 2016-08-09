"""
This module supports to do the functions under ruckus(config)# and ruckus(config-mdnsproxyrule)#
mode of ZDCLI:

Commands available for :
  mdnsproxy    Enables mdnsproxy.
  no mdnsproxy       Disables mdnsproxy.
  show mdnsproxy       Shows mdnsproxy value.
  
  mdnsproxyrule {raw_id}       Add or edit services rules.
  show mdnsproxyrule {<id-from><id-to>}      Shows mdnsproxy services rules.
  no mdnsproxyrule [id|<service-name><from-vlan><to-vlan>]       Deletes a restrict services rule.
  
---Created by ye.songnan, 2013.09.04
"""


import re
import logging
from string import Template
from pprint import pformat
from RuckusAutoTest.components.lib.zdcli import output_as_dict
#
# GLOBAL DEFINATION
#

ENABLE_BONJOUR_GW = "mdnsproxy zd\n"
DISABLE_BONJOUR_GW = "no mdnsproxy zd\n"

SET_RULE = "mdnsproxyrule\n"
EDIT_RULE = "mdnsproxyrule $id\n"
SET_SERVICES_TYPE = "service $service\n"
SET_FROM_VLAN = "from-vlan $from_vlan\n"
SET_TO_VLAN = "to-vlan $to_vlan\n"
SET_NOTE = "note $note\n"
DELETE_RULE = "no mdnsproxyrule $id\n"

SHOW_RULE_ALL = "show mdnsproxyrule\n"
SHOW_RULE_RANGE = "show mdnsproxyrule $id_from $id_to\n"

SAVE_CFG = "exit\n"

########################################################################################
# PUBLIC SECSSION
########################################################################################

def enable_bonjour_gateway(zdcli):
    '''
    ruckus(config)# mdnsproxy
    Mdnsproxy is successfully started.
    
    '''
    cmd_block = ENABLE_BONJOUR_GW
    res = zdcli.do_cfg(cmd_block, raw=True, timeout = 20)
    logging.info('cmd_block execution result:\n%s' % res)
    return res
    
def disable_bonjour_gateway(zdcli):
    '''
    ruckus(config)# no mdnsproxy
    Bonjour Gateway is successfully closed.
    
    '''
    cmd_block = DISABLE_BONJOUR_GW
    res = zdcli.do_cfg(cmd_block, raw=True, timeout = 20)
    logging.info('cmd_block execution result:\n%s' % res)
    return res
  
def get_bonjour_gateway_value(zdcli):
    '''
    bonjour_gw_value : 'disabled' or 'enabled'
    
    '''
    info = _show_bonjour_gateway(zdcli)
    info_dict = output_as_dict.parse(info)
    '''
    info_dict
    {'The AP mdnsproxy status ': {'disabled': ''}, 'The mdnsproxy status ': {'disabled': ''}}
    '''
    #bonjour_gw_value = info.split(':')[1].strip()
    if info_dict.has_key('The mdnsproxy status '):
        bonjour_gw_value = info_dict['The mdnsproxy status '].keys()[0]
    else:
        raise Exception('Error, not able to get mdnsproxy status')
    return bonjour_gw_value 
def get_services_rule(zdcli, id_from='', id_to=''):
    '''      
    Generate a list with rule dictionary.
    
    '''
    output = _show_services_rule(zdcli, id_from, id_to)
    rule_list = _parse_services_rule(output)
    return rule_list

def get_rule_nums(zdcli):
    '''
    Get the numbers of services rules.
    
    '''
    nums = len(get_services_rule(zdcli))
    return nums

def new_services_rule(zdcli, service, from_vlan, to_vlan, note=''):
    '''
    Add a new services rule.
    
    Return True, if create it successfully.
    Return False, if create if fail.
    
    '''
    return _cfg_services_rule(zdcli, service, from_vlan, to_vlan, note)

def edit_services_rule(zdcli, service, from_vlan, to_vlan, rule_id, note=''):
    '''
    Edit the existed rule by rule id.
    
    Return True, if edit it successfully.
    Return False, if edit if fail.
    
    '''
    return _cfg_services_rule(zdcli, service, from_vlan, to_vlan, note, rule_id)

def remove_services_rule(zdcli, rule_id):
    '''
    Remove the services by rule id.

    Return True, if remove it successfully.
    Return False, if remove if fail.   
    '''
    return _del_services_rule(zdcli, rule_id)

def remove_all_services_rule(zdcli):
    '''
    Remove all services rules.

    Return True, if remove it successfully.
    Return False, if remove if fail.   
    '''
    rule_list = get_services_rule(zdcli)
    value = True
    res = ''
    if len(rule_list) == 0:
        return (value,res)
    rule_id_list = [item['id'] for item in rule_list]
    for rule_id in rule_id_list:
        (value, res) = _del_services_rule(zdcli, rule_id)
        if value == False:
            break
            #return (value,res)
    return (value,res)   
            #raise Exception("Del rule %s failed: \n%s" %(item_dict['id'], res))   

def get_services_rule_id(zdcli, service, from_vlan, to_vlan, id_from='', id_to=''):
    '''
    Get rule id by service_name, from_vlan, and to_vlan.
    
    Return rule id, if input is right.
    Raise exception, if can't get rule id.
    
    '''
#    'service_name': 'Apple Mobile Devices (Allows Sy',---bug #ZF-5055 .Use [:30] to avoid this.
    rule_list = get_services_rule(zdcli, id_from, id_to)
    for item_dict in rule_list:
        if (item_dict['from_vlan'], item_dict['to_vlan'], item_dict['service_name'][:30]) == (from_vlan, to_vlan, service[:30]):
            return item_dict['id']
    raise Exception("Can't get the rule id, please check your input")    

def map_names_types():
    '''
    output:
        {'AirDisk': '_adisk._tcp.',
         'AirPlay': '_airplay._tcp.',
         'AirPort Management': '_airport._tcp.',
         'AirPrint': '_ipp._tcp.',
         'AirTunes': '_raop._tcp.',
         'Apple File Sharing': '_afpovertcp._tcp.',
         'Apple Mobile Devices (Allows Sync with iTunes over Wi-Fi)': '_apple-mobdev._tcp.',
         'Apple TV': '_appletv-v2._tcp.',
         'Open Directory Master': '_od-master._tcp.',
         'Optical Disk Sharing': '_odisk._tcp.',
         'Ruckus Controller': '_ruckus-zd._tcp.',
         'Screen Sharing': '_rfb._tcp.',
         'Secure File Sharing': '_sftp-ssh._tcp.',
         'Secure Shell (SSH)': '_ssh._tcp.',
         'Workgroup Manager': '_workstation._tcp.',
         'World Wide Web (HTTP)': '_http._tcp.',
         'World Wide Web SSL (HTTPS)': '_https._tcp.',
         'Xgrid': '_xgrid._tcp.',
         'iCloud Sync': '_ubd._tcp.',
         'iTunes Remote': '_dacp._tcp.',
         'iTunes Sharing': '_home-sharing._tcp.'}
 
    '''
    service_name = ("AirDisk", "AirPlay", "AirPort Management", "AirPrint", "AirTunes", 
                    "Apple File Sharing", "Apple Mobile Devices (Allows Sync with iTunes over Wi-Fi)",
                    "Apple TV", "iCloud Sync", "iTunes Remote", "iTunes Sharing",
                    "Open Directory Master", "Optical Disk Sharing", "Ruckus Controller", "Screen Sharing",
                    "Secure File Sharing", "Secure Shell (SSH)", "World Wide Web (HTTP)", "World Wide Web SSL (HTTPS)",
                    "Workgroup Manager", "Xgrid")
    service_type = ("_adisk._tcp.", "_airplay._tcp.", "_airport._tcp.", "_ipp._tcp.", "_raop._tcp.",
                    "_afpovertcp._tcp.", "_apple-mobdev._tcp.",
                    "_appletv-v2._tcp.", "_ubd._tcp.", "_dacp._tcp.", "_home-sharing._tcp.",
                    "_od-master._tcp.", "_odisk._tcp.", "_ruckus-zd._tcp.", "_rfb._tcp.",
                    "_sftp-ssh._tcp.", "_ssh._tcp.", "_http._tcp.", "_https._tcp.",
                    "_workstation._tcp.", "_xgrid._tcp.")
    dict_names_types = dict(zip(service_name, service_type))
    
    return dict_names_types

########################################################################################
# PRIVATE SECSSION
########################################################################################

def _show_bonjour_gateway(zdcli):
    '''
    ruckus(config)# show mdnsproxy
    The mdnsproxy status : disabled
    
    res = ['The mdnsproxy status : disabled']
    '''
    res = zdcli.do_show("mdnsproxy", go_to_cfg = True, timeout = 20)
    logging.info('show bonjour gateway result:\n%s' % res[0])
    return res[0]

def _show_services_rule(zdcli, id_from='', id_to=''):
    '''      
    ruckus(config)# show mdnsproxyrule
    ------------------------------------------------------------------------
    ID  service-name                    vlan_from   vlan_to     note                                                            
    ------------------------------------------------------------------------
    1   Apple TV                        10          20          hhh                                                             
    2   AirPrint                        1           2                                                                           
    ------------------------------------------------------------------------
    OR
    ruckus(config)# show mdnsproxyrule 1 2
    ------------------------------------------------------------------------
    ID  service-name                    vlan_from   vlan_to     note                                                            
    ------------------------------------------------------------------------
    1   Apple TV                        10          20          hhh                                                             
    2   AirPrint                        1           2                                                                           
    ------------------------------------------------------------------------    
    
    '''
    if id_from and id_to:
        if id_from <= id_to:
            cmd_block = Template(SHOW_RULE_RANGE).substitute({'id_from':id_from, 'id_to':id_to})
        else:
            raise Exception('The useage is error: id_from should less than id_to')
    else:
        cmd_block = SHOW_RULE_ALL
    logging.info( "=======show services rule=========")
    res = zdcli.do_show(cmd_block, go_to_cfg = True, timeout = 20)
    logging.info('show services rule result:\n%s' % res[0])
    return res[0]

def _parse_services_rule(output):
    '''
    output:
    
    [{'id': 1,
      'note': '',
      'service_name': 'AirDisk',
      'from_vlan: 2,
      'to_vlan': 1},
     {'id': 2,
      'note': 'this is just for a test',
      'service_name': 'World Wide Web SSL (HTTPS)',
      'from_vlan': 200,
      'to_vlan': 100}]
    
    '''
    pattern = re.compile(r'(\d+)\s*([a-zA-Z]+(?:\s[a-zA-Z()]+)*|_.*_tcp.)\s+(\d+)\s+(\d+)\s+(.*)')
    temp_list = output.split('\r\n')
    services_rule_list = []
    for item in temp_list:
        m = pattern.match(item)
        if m:
            rule_item = dict(
                             id = int(m.group(1)),
                             service_name = m.group(2),
                             from_vlan = int(m.group(3)),
                             to_vlan = int(m.group(4)),
                             note = m.group(5).strip()
                             )
            services_rule_list.append(rule_item)
    return services_rule_list
    
def _cfg_services_rule(zdcli, service, from_vlan, to_vlan, note='', rule_id=''):
    '''
    ruckus(config)# mdnsproxyrule 
    ruckus(config-mdnsproxyrule)# service AirPlay 
    ruckus(config-mdnsproxyrule)# from-vlan 1
    ruckus(config-mdnsproxyrule)# to-vlan 2
    ruckus(config-mdnsproxyrule)# note "test"
    ruckus(config-mdnsproxyrule)# exit
    Your changes have been saved.
    
    '''
    if rule_id:
        cmd_block = Template(EDIT_RULE).substitute({'id':rule_id})
    else:
        cmd_block = SET_RULE 
    cmd_block += Template(SET_SERVICES_TYPE).substitute({'service':pformat(service)})
    cmd_block += Template(SET_FROM_VLAN).substitute({'from_vlan':from_vlan})
    cmd_block += Template(SET_TO_VLAN).substitute({'to_vlan':to_vlan})
    cmd_block += Template(SET_NOTE).substitute({'note':pformat(note)})
    cmd_block += SAVE_CFG
    res = zdcli.do_cfg(cmd_block, raw=True, timeout = 20)
    logging.info('cmd_block execution result:\n%s' % res)
    if "Your changes have been saved." not in res['exit'][0]:
        zdcli.back_to_priv_exec_mode(back_cmd = 'abort', print_out = True)#chen.tao 2014-04-21,to fix ZF7911
        return (False, res)
    return (True, "")

def _del_services_rule(zdcli, rule_id):
    '''
    ruckus(config)# no mdnsproxyrule 1
    The rule have been successfully deleted.

    '''
    cmd_block = Template(DELETE_RULE).substitute({'id':rule_id})
    res = zdcli.do_cfg(cmd_block, raw=True, timeout = 20)
    logging.info('cmd_block execution result:\n%s' % res)
    #if "The rule have been successfully deleted." not in res['no mdnsproxyrule %s' %rule_id][0]:
    if "Operation done" not in res['no mdnsproxyrule %s' %rule_id][0]:
        return (False, res)
    return (True, "")