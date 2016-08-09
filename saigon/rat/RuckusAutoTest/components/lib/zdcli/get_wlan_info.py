"""
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""

import copy
import logging
from string import Template
from pprint import pformat

from RuckusAutoTest.components.lib.zdcli import output_as_dict


# Command templates
GET_WLAN_ALL= "show wlan all"
GET_WLAN_BY_NAME= "show wlan name '$ssid'"
SSID_ERR_MSG = "The entry '$ssid' could not be found. Please check the spelling, and then try again."

#GUI wlan configuration
GUI_CONF = {
    'ssid': None, 
    'description': None, 
    'auth': '', 
    'type': 'standard',
    'wpa_ver': '', 
    'encryption': '', 
    'key_string': '', 
    'key_index': '', 
    'auth_svr': '',
    'do_webauth': None, 
    'do_isolation': None, 
    'do_zero_it': None,
    'acct_svr': '', 
    'interim_update': None, 
    'acl_name': '', 
    'l3_l4_acl_name': '', 
    'uplink_rate_limit': '', 
    'downlink_rate_limit': '', 
    'vlan_id': None, 
    'dvlan': False,
    'do_hide_ssid': None, 
    'do_tunnel': None, 
    'hotspot_profile': '',
    'do_dynamic_psk': None,
    }
 
#CLI wlan information template
#CLI_WLAN_INFO_template = {
#    'SSID': '',
#    'Description': '',
#    'Authentication': 'open',
#    'Encryption': 'none',
#    'L2/MAC': 'No ACLS',
#    'Rate Limiting Downlink': 'Disabled',
#    'Rate Limiting Uplink': 'Disabled',
#    'VLAN': 'Disabled',
#    'Dynamic VLAN': 'Disabled',
#    'Closed System': 'Disabled',
#    'Tunnel Mode': 'Disabled',
# 
#    'Algorithm': 'auto',
#    'Passphrase': '',
#    'WEP Key': '',
#    'WEP Key Index': '',
#    'Hotspot Services': '',
#    'Web Authentication': 'Disabled',
#    'Authentication Server': 'Disabled',
#    'Client Isolation': 'None',
#    'Zero-IT Activation': 'Disabled',
#    'Accounting Server': 'Disabled',
#    'Interim Update': 'Disabled',
#    'L3/L4/IP Address': 'No ACLS',

#    'Background Scanning': 'Enabled',
#    'Load Balancing': 'Enabled',
#    'Max Clients': '100',
#    'Priority': 'High',
#    }


def get_wlan_by_ssid(zdcli, ssid):
    """
    Output:
            a dictionary of the wlan information:
            {
             'SSID':
             'Description':
             ...
            }
            none: the wlan does not exist.
            raise exception
    """
    cmd = Template(GET_WLAN_BY_NAME).substitute(dict(ssid = ssid))
    ssid_err_msg = Template(SSID_ERR_MSG).substitute(dict(ssid = ssid))
    
    logging.info('Get information of wlan [%s] from zd CLI by command [%s]' % (ssid, cmd))
    try:
        info = _get_wlan_info_as_dict(zdcli, cmd)
        
    except Exception, ex:
        if ssid_err_msg in ex.message:
            logging.info('The wlan [%s] does not exist!' % ssid)
            return None
        else:
            raise Exception(ex.message)
    
    wlan_info = info.values()[0]
    logging.info('Information of wlan [%s] in ZD CLI:\n%s' % (ssid, pformat(wlan_info, 4, 120)))

    return wlan_info

def get_max_clients_number(zdcli,ssid):
    return get_wlan_by_ssid(zdcli, ssid)['Max. Clients']

def get_wlan_all(zdcli):
    """
    Output:
            a dictionary of all wlan information:
            {
             '1': {
                   'SSID':
                   'Description':
                   ...
                   },
             '2': {
                   'SSID':
                   'Description':
                   ...
                   },
             ...
            }
            none: no wlan exists in zdcli.
            raise exception
    """
    
    logging.info('Get all wlan information from ZD CLI by command [%s]' % GET_WLAN_ALL)
    wlan_info = _get_wlan_info_as_dict(zdcli, GET_WLAN_ALL)
    
    if wlan_info:
        logging.info("All wlan information in ZD CLI:\n%s" % pformat(wlan_info, 4, 120))
    else:
        logging.info("Does't find any wlan in ZD CLI")
    
    return wlan_info 


#stan@20110120
def get_all_wlan_name_list(zdcli):
    wlan_name_list = []
    info_dict = _get_wlan_info_as_dict(zdcli, GET_WLAN_ALL)
    if info_dict:
        info_list = info_dict.values()
        for i in range(len(info_list)):
            wlan_name = info_list[i]['SSID']
            wlan_name_list.append(wlan_name)
    
    return wlan_name_list


def verify_wlan_info(cli_info, gui_conf):
    logging.info('Verify the wlan information shown in ZD CLI.')
    
    if cli_info == None:
        if gui_conf == None:
            logging.info('No wlan exists in CLI or GUI')
            return True
        else:
            logging.info('The wlan [%s] exists in GUI but not in CLI' % gui_conf['ssid'])
            return False
    else:
        if gui_conf == None:
            logging.info('The wlan [%s] exists in CLI but not in GUI' % cli_info['SSID'])
            return False
        
    gui_info = _define_expected_result_from_gui_conf(gui_conf)
    
    return _verify_wlan_info(cli_info, gui_info)

    
def verify_wlan_info_all(cli_info_dict, gui_conf_list):
    logging.info('Verify all wlan information shown in ZD CLI.')
    
    if cli_info_dict == None:
        if gui_conf_list == None:
            logging.info('No wlan exists in CLI or GUI')
            return True
        else:
            logging.info('There are wlans in GUI but not in CLI')
            return False
    else:
        if gui_conf_list == None:
            logging.info('There are wlans in CLI but not in GUI')
            return False
    
    cli_info_list =  cli_info_dict.values()
    
    cli_len = len(cli_info_list)
    gui_len = len(gui_conf_list)

    if cli_len != gui_len:
        logging.info('The number of wlans in CLI [%s] is not the same as in GUI [%s]' % (cli_len, gui_len))
        return False
    
    for i in range(cli_len):
        for j in range(gui_len):
            if cli_info_list[i]['SSID'] == gui_conf_list[j]['ssid']:
                
                gui_info = _define_expected_result_from_gui_conf(gui_conf_list[j])
                res = _verify_wlan_info(cli_info_list[i], gui_info)
                if not res:
                    return False
                else:
                    break
            elif j == gui_len - 1:
                logging.info('The wlan [%s] exists in CLI, but not in GUI' % cli_info_list[i]['SSID'])
                return False
            
    logging.info('All wlan information in CLI is correct')
    return True
        
                
def _get_wlan_info_as_dict(zdcli, cmd):
    data = zdcli.do_show(cmd)
    if not data.startswith("WLAN Service:"):
        raise Exception(data)
                        
    info = output_as_dict.parse(data)
    if not info:
        return None

    else:
        return info['WLAN Service']['ID']


def _verify_wlan_info(cli_info, gui_info):
    cli_ks = cli_info.keys()
    gui_ks = gui_info.keys()
    
    for k in gui_ks:
        if k not in cli_ks:
            logging.info('The parameter [%s] of wlan [%s] exists in GUI but not in CLI' % (k, gui_info['SSID']))
            return False
        
        if cli_info[k] != gui_info[k]:
            logging.info("The information of wlan [%s] in CLI [%s = %s] is not the same as in GUI [%s = %s]" % (cli_info['SSID'], k, cli_info[k], k, gui_info[k]))
            return False
        
    logging.info('The information of wlan [%s] in CLI is correct!' % cli_info['SSID'])
    return True


def _define_expected_result_from_gui_conf(gui_conf):
    logging.info('The wlan configuration in GUI is: \n%s' % pformat(gui_conf, 4, 120))
    
    conf = copy.deepcopy(GUI_CONF)
    conf.update(gui_conf)
    info = {}

    if conf['ssid'] is not None:
        info['SSID'] = conf['ssid']

    if conf['description'] is not None:
        info['Description'] = conf['description']
    else:
        info['Description'] = ''

    if conf['type'] == "guest":
        info['Authentication Server'] = 'Guest Accounts'     
        if conf['do_isolation'] is not None:
            info['Client Isolation'] = conf['do_isolation']
        else:
            info['Client Isolation'] = 'Full'
    
    elif conf['type'] == "hotspot":
        info['Authentication Server'] = 'Local Database'
        if conf['hotspot_profile']:
            info['Hotspot Services'] = conf['hotspot_profile']
    
    else:
        if conf['auth_svr']:
            info['Authentication Server'] = conf['auth_svr']
        
        if conf['do_isolation'] is not None:
            info['Client Isolation'] = conf['do_isolation']
        else:
            info['Client Isolation'] = 'None'

    if conf['auth']:
        if conf['auth'] == 'PSK':
            info['Authentication'] = 'open'
        elif conf['auth'] == 'EAP':
            info['Authentication'] = '802.1x-eap'
        else:
            info['Authentication'] = conf['auth'].lower()
    else:
        info['Authentication'] = 'open'
        
    if conf['wpa_ver']:
        info['Encryption'] = conf['wpa_ver'].lower()
        if conf['encryption'] in ['TKIP', 'AES', 'Auto']:
            info['Algorithm'] = conf['encryption'].lower()
        info['Passphrase'] = conf['key_string']
        
    elif conf['encryption'] in ['WEP-64', 'WEP-128']:
        info['Encryption'] = conf['encryption'].replace('-', '').lower()
        if conf['key_index']:
            info['WEP Key Index'] = conf['key_index']
        info['WEP Key'] = conf['key_string']

    elif conf['encryption'] == 'none':
        info['Encryption'] = 'none'
 
    if conf['do_zero_it'] is not None:
        if conf['do_zero_it']:
            info['Zero-IT Activation'] = 'Enabled'
        else:
            info['Zero-IT Activation'] = 'Disabled'
        
    if conf['do_webauth'] is not None:
        if conf['do_webauth']:
            info['Authentication'] = 'Enabled'
        else:
            info['Authentication'] = 'Disabled'
    
    if conf['acct_svr']:
        info['Accounting Server'] = conf['acct_svr']

    if conf['interim_update'] is not None:
        info['Interim Update'] = conf['interim_update']
        
    if conf['acl_name']:
        info['L2/MAC'] = conf['acl_name']
  
    if conf['l3_l4_acl_name']:
        info['L3/L4/IP Address'] = conf['l3_l4_acl_name']

    if conf['uplink_rate_limit']:
        info['Rate Limiting Uplink'] = conf['uplink_rate_limit']

    if conf['downlink_rate_limit']:
        info['Rate Limiting Downlink'] = conf['downlink_rate_limit']

    if conf['vlan_id'] is not None:
        info['VLAN'] = conf['vlan_id']

    if conf['dvlan']:
        info['Dynamic VLAN'] = 'Enabled'
    else:
        info['Dynamic VLAN'] = 'Disabled'
 
    if conf['do_hide_ssid'] is not None:
        if conf['do_hide_ssid']:
            info['Closed System'] = 'Enabled'
        else:
            info['Closed System'] = 'Disabled'

    if conf['do_tunnel'] is not None:
        if conf['do_tunnel']:
            info['Tunnel Mode'] = 'Enabled'
        else:
            info['Tunnel Mode'] = 'Disabled'
            
    logging.info('The expected wlan information in CLI is: \n%s' % pformat(info, 4, 120))
    return info

