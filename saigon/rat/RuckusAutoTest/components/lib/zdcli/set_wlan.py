import logging
import re
import time
import os
from string import Template

from RuckusAutoTest.components.lib.zdcli import output_as_dict as output
from RuckusAutoTest.components.lib.zdcli import configure_guestaccess as guest_access
from RuckusAutoTest.components.lib.zdcli import configure_hotspot as hotspot

import get_wlan_info as wlangetter

CREATE_WLAN = """
wlan '$name'
"""
DELETE_WLAN = """
no wlan '$name'
"""
#@author:yanan.yu @since:2014-4-19 @change:adapt to 9.10 self-service guestpass
SET_NAME = """
wlan '$name'
    name '$newname'
"""
SET_SSID = """
wlan '$name'
    ssid '$ssid'
"""
SET_DESCRIPTION = """
wlan '$name'
    description '$description'
"""
SET_NAS_ID_TYPE = """
wlan '$name'
    nasid-type $type
"""
SET_NAS_ID_TYPE_USER_DEF = """
wlan '$name'
    nasid-type $type $value
"""

SET_CALLED_STA_ID_TYPE = """
wlan '$name'
    called-station-id-type $type
"""

SET_TYPE_HOTSPOT = """
wlan '$name'
    type hotspot '$hotspot_name'
"""
#@author: Jane.Guo @since: 2013-09 adapt to 9.8 Guest Access improvement
SET_TYPE_GUEST = """
wlan '$name'
    type guest-access '$guest_name'
"""
SET_TYPE_AUTONOMOUS = """
wlan '$name'
    type autonomous
"""
 
SET_TYPE_STANDARD= """
wlan '$name'
    type standard-usage
"""
SET_TYPE = """
wlan '$name'
    type $type $service
"""

SET_OPEN_NONE = """
wlan '$name'
    open none
"""

SET_WEP_CONF = """
wlan '$name'
    $authentication $encryption key $key_string key-id $key_index
"""

SET_WPA_CONF = """
wlan '$name'

    $authentication $encryption passphrase $passphrase algorithm $algorithm
"""

SET_MAC_NONE = """
wlan '$name'
    mac none auth-server '$auth_server'
"""

SET_MAC_WEP_CONF = """
wlan '$name'
    mac $encryption key $key_string key-id $key_index auth-server '$auth_server'
"""

SET_MAC_ADDR_FORMAT = """
wlan '$name'
    mac-addr-format $mac_addr_format
"""

SET_MAC_WPA_CONF ="""
wlan '$name'
    mac $encryption passphrase $passphrase algorithm $algorithm auth-server '$auth_server'
"""

SET_DOT1X_WEP_CONF = """
wlan '$name'
    dot1x $encryption auth-server name '$auth_server'
"""

SET_DOT1X_WEP_CONF_LOCAL = """
wlan '$name'
    dot1x $encryption auth-server local     
"""


SET_DOT1X_WPA_CONF = """
wlan '$name'
    dot1x $encryption algorithm $algorithm auth-server name '$auth_server'
"""
SET_DOT1X_WPA_CONF_LOCAL = """

wlan '$name'
    dot1x $encryption algorithm $algorithm auth-server local
"""

SET_DOT1X_EAP_CONF = """
wlan '$name'
    dot1x eap-type $eap_type auth-server name '$auth_server'
"""

SET_DOT1X_EAP_CONF_LOCAL = """
wlan '$name'
    dot1x eap-type $eap_type auth-server local
"""

SET_DOT1X_MAC_CONF = """
wlan '$name'
    dot1x-mac none auth-server name '$auth_server'
"""

SET_WEB_AUTH = """
wlan '$name'
    web-auth name '$auth_server'
"""

SET_WEB_AUTH_LOCAL = """
wlan '$name'
    web-auth local
"""

DISABLE_WEB_AUTH = """
wlan '$name'
    no web-auth
"""

SET_CLIENT_ISOLATION = """
wlan '$name'
    client-isolation $isolation
"""

DISABLE_CLIENT_ISOLATION = """
wlan '$name'
    no client-isolation
"""

#@author: Jane.Guo @since: 2013-7-11 start/add to support new implementation of client isolation in 9.7
SET_CLIENT_ISOLATION_ON_AP = """
wlan '$name'
    client-isolation isolation-on-ap $enable
"""

#@author: Jane.Guo @since: 2013-09 adapt to 9.8
SET_CLIENT_ISOLATION_ACROSS_AP = """
wlan '$name'
    client-isolation isolation-on-subnet $enable
"""

SET_WHITE_LIST = """
wlan '$name'
    client-isolation isolation-on-subnet $enable
    whitelist name '$white_list'
"""

SET_NO_WHITE_LIST = """
wlan '$name'
    no whitelist
"""
ENABLE_SET = 'enable'
DISABLE_SET = 'disable'
#@author: Jane.Guo @since: 2013-7-11 end/

ENABLE_ZERO_IT = """
wlan '$name'
    zero-it-activation
"""

DISABLE_ZERO_IT = """
wlan '$name'
    no zero-it-activation
"""

ENABLE_DPSK = """
wlan '$name'
    dynamic-psk enable
"""

#@author: yin.wenling @since: 2014-09 adapt to 9.9 Mobile Friendly
ENABLE_MOBILE_FRIENDLY = """
    wlan '$name'
    dynamic-psk type mobile-friendly
"""

SET_PRIOTITY = """
wlan '$name'
    priority $priority
"""

SET_ACCOUNTING = """
wlan '$name'
    acct-server $acct_server interim-update $interim
"""
SET_NO_ACCT_SERVER = """
wlan '$name'
    no acct-server
"""
SET_L2ACL = """
wlan '$name'
    acl l2acl '$l2acl_name'
"""

DISABLE_L2ACL = """
wlan '$name'
    no l2acl
"""

SET_L3ACL = """
wlan '$name'
    acl l3acl '$l3acl_name'
"""

SET_L3ACL_IPV6 = """
wlan '$name'
    acl l3acl-ipv6 '$l3acl_ipv6_name'
"""

DISABLE_L3ACL = """
wlan '$name'
    no l3acl
"""

SET_RATE_LIMIT = """
wlan '$name'
    rate-limit uplink $rate_limit_uplink downlink $rate_limit_downlink
"""

ENABLE_RBAC = """
wlan '$name'
    acl role-based-access-ctrl
    dynamic-vlan
"""

ENABLE_VLAN_POOL = """
wlan '$name'
    vlanpool $vlan_pool_name
"""
SET_VLAN = """
wlan '$name'
    vlan $vlan_id
"""

DISABLE_VLAN = """
wlan '$name'
    vlan 1
    no vlan
"""

ENABLE_HIDE_SSID = """
wlan '$name'
    hide-ssid
"""

DISABLE_HIDE_SSID = """
wlan '$name'
    no hide-ssid
"""

ENABLE_TUNNEL_MODE = """
wlan '$name'
    tunnel-mode
"""

DISABLE_TUNNEL_MODE = """
wlan '$name'
    no tunnel-mode
"""

ENABLE_PROXY_ARP = """
wlan '$name'
    proxy-arp
"""

DISABLE_PROXY_ARP = """
wlan '$name'
    no proxy-arp
"""

ENABLE_BGSCAN = """
wlan '$name'
    bgscan
"""

DISABLE_BGSCAN = """
wlan '$name'
    no bgscan
"""

ENABLE_IGNORE_UNAUTH_STATS = """
wlan '$name'
    ignor-unauth-stats
"""
DISABLE_IGNORE_UNAUTH_STATS = """
wlan '$name'
    no ignor-unauth-stats
"""

ENABLE_LOAD_BALANCING = """
wlan '$name'
    load-balancing
"""

DISABLE_LOAD_BALANCING = """
wlan '$name'
    no load-balancing
"""

SET_MAX_CLIENT = """
wlan '$name'
     max-clients $max_client
"""
ENABLE_DVLAN_COMMAND = """    dynamic-vlan
"""
ENABLE_DYNAMIC_VLAN = """
wlan '$name'
    dynamic-vlan
"""

DISABLE_DYNAMIC_VLAN = """
wlan '$name'
    no dynamic-vlan
"""

#serena
SET_GRACE_PERIOD = """
wlan '$name'
     grace-period $grace_period
"""

DISABLE_GRACE_PERIOD = """
wlan '$name'
    no grace-period
"""

#@author: Liu Anzuo @since: 20130925 to add a "end" to option82 cmd for 9.8
ENABLE_OPTION82 = """
wlan $name
    option82
    end
"""

DISABLE_OPTION82 = """
wlan $name
    no option82
    end
"""

SUBOPT1 = """
option82
    subopt1 $item
    end
"""
SUBOPT2 = """
option82
    subopt2 $item
    end
"""
SUBOPT150 = """
option82
    subopt150 $item
    end
"""
SUBOPT151 = """
option82
    subopt151 $item
    end
"""
#@author: Jane.Guo 
#@since: 2013-5-8 to Add CLI command for Force DHCP
ENABLE_FORCE_DHCP = """
wlan '$name'
    force-dhcp
"""

DISABLE_FORCE_DHCP = """
wlan '$name'
    no force-dhcp
"""

FORCE_DHCP_TIMEOUT = """
wlan '$name'
    force-dhcp-timeout $force_dhcp_timeout
"""

DISABLE_FORCE_DHCP_TIMEOUT = """
wlan '$name'
    no force-dhcp
"""

ENABLE_FINGERPRINTING = """
wlan '$name'
    sta-info-extraction
"""

DISABLE_FINGERPRINTING = """
wlan '$name'
    no sta-info-extraction
"""

#@author: Anzuo, @change: enable dynamic-vlan with device policy
ENABLE_DEVICE_POLICY = """
wlan '$name'
    acl dvcpcy '$dvcpcy_name'
    dynamic-vlan
"""

#@author: Anzuo, @change: disable dynamic-vlan with device policy
DISABLE_DEVICE_POLICY = """
wlan '$name'
    no dvcpcy
    no dynamic-vlan
"""

DISABLE_DEVICE_POLICY_ONLY = """
wlan '$name'
    no dvcpcy
"""
ENABLE_PRECEDENCE_POLICY = """
wlan '$name'
    acl prece '$prece_name'
"""

SAVE_SERVER_CONFIG = "\nexit\n"
DEFAULT_GC_NAME = "Guest_Access_Default"
DEFAULT_HS_NAME = "Hotsport_Default"

SUBOPTITEM1 = ['rks-circuitid', 'ap-mac-hex', 'ap-mac-hex-essid', 'disable']
SUBOPTITEM2 = ['client-mac-hex', 'client-mac-hex-essid', 'ap-mac-hex', 'ap-mac-hex-essid', 'disable']
SUBOPTITEM150 = ['vlan-id', 'disable']
SUBOPTITEM151 = ['essid', 'area-name', 'disable']

def _adapter_between_gui_and_cli(conf):
    if conf['name'] is None:
        conf['name'] = conf['ssid']

    if (not conf['hotspot_name']) and conf.get('hotspot_profile'):
        conf['hotspot_name'] = conf['hotspot_profile']

    if (not conf['web_auth']) and conf.get('do_webauth'):
        conf['web_auth'] = conf['do_webauth']
        
    if (not conf['zero_it']) and conf.get('do_zero_it'):
        conf['zero_it'] = conf['do_zero_it']

    if (not conf['client_isolation']) and conf.get('do_isolation'):
        conf['client_isolation'] = conf['do_isolation']

    if (not conf['hide_ssid']) and conf.get('do_hide_ssid'):
        conf['hide_ssid'] = conf['do_hide_ssid']

    if (not conf['rate_limit_uplink']) and conf.get('uplink_rate_limit'):
        conf['rate_limit_uplink'] = conf['uplink_rate_limit']

    if (not conf['rate_limit_downlink']) and conf.get('downlink_rate_limit'):
        conf['rate_limit_downlink'] = conf['downlink_rate_limit']

    if (not conf['auth_server']) and conf.get('auth_svr'):
        conf['auth_server'] = conf['auth_svr']

    if (not conf['acc_server']) and conf.get('acct_server'):
        conf['acc_server'] = conf['acct_server']
        if (not conf['interim']) and conf.get('interim_update'):
            conf['interim'] = conf['interim_update']
            
    if (not conf['tunnel_mode']) and conf.get('do_tunnel'):
        conf['tunnel_mode'] = conf['do_tunnel']

    if conf.get('do_grace_period'):
        if conf['do_grace_period'] is True:
            if (not conf['grace_period']):
                conf['grace_period'] = '30' # default value
        else:
            if (not conf['grace_period']):
                conf['grace_period'] = False

    if (not conf['l2acl']) and conf.get('acl_name'):
        conf['l2acl'] = conf['acl_name']

    if (not conf['l3acl']) and conf.get('l3_l4_acl_name'):
        conf['l3acl'] = conf['l3_l4_acl_name']

    if (not conf['l3acl_ipv6']) and conf.get('l3_l4_ipv6_acl_name'):
        conf['l3acl_ipv6'] = conf['l3_l4_ipv6_acl_name']
        
    if conf['type'].lower() == 'standard':
        conf['type'] = "standard-usage"
        
    if conf['auth'].lower() == 'psk':
        conf['auth'] = 'open'
    elif conf['auth'].lower() == 'eap':
        conf['auth'] = 'dot1x-eap'
        if conf['eap_type'] is None:
            conf['eap_type'] = 'PEAP'
    elif conf['auth'].lower() == 'maceap' or conf['auth'].lower() == 'mac-eap' or conf['auth'].lower() == 'mac_eap':
        conf['auth'] = 'dot1x-mac'

    if conf.get('wpa_ver'):
        if conf['encryption']:
            conf['algorithm'] = conf['encryption'].lower()
        conf['encryption'] = conf['wpa_ver'].lower()

    if conf['encryption'].lower() == 'wpa_mixed' or conf['encryption'].lower() == 'wpa-mixed' or conf['encryption'].lower() == 'wpamixed':
        conf['encryption'] = 'wpa-mixed'
    elif conf['encryption'].lower() == 'wep64' or conf['encryption'].lower() == 'wep-64' or conf['encryption'].lower() == 'wep_64':
        conf['encryption'] = 'wep-64'
    elif conf['encryption'].lower() == 'wep128' or conf['encryption'].lower() == 'wep-128' or conf['encryption'].lower() == 'wep_128':
        conf['encryption'] = 'wep-128'

    if conf['encryption'] in ['wpa', 'wpa2', 'wpa-mixed']:
        if conf['key_string']:
            conf['passphrase'] = conf['key_string']

def create_wlan(zdcli, wlan_conf):
    """
    Setting wlan configuration via ZD CLI using input paramters. 
    
    """
    conf = {
            'name':None,
            'newname':None,
            'ssid': None,
            'description': None,

            'type': 'Standard',  #None, @zj 20140724 ZF-9365
            'hotspot_name': '',

            'auth': '', #Authentication
            'encryption': '',
            'key_string': '',
            'key_index': '',
            'passphrase':'',
            'auth_server': '',
            'algorithm':'',
            'eap_type':None,

            'web_auth': None,
            'client_isolation': None,
            'zero_it': None,
            'enable_dpsk':None,
            'priority':'',

            'acc_server':None,
            'interim':None,
            'l2acl':None,
            'l3acl': None,
            'l3acl_ipv6': None,
            'rate_limit_uplink': '',
            'rate_limit_downlink': '',
            'vlan':None,
            'vlan_id':None,
            'hide_ssid':None, # Closed System
            'tunnel_mode': None,
            'do_proxy_arp': None,
            'bgscan':None,
            'ignore_unauth':None,
            'load_balance':None,
            'max_clients':None,
            'dvlan': None,
            'grace_period': None,
            'option82': None,
            'force_dhcp': None,
            'force_dhcp_timeout': None,  
            'fingerprinting':None,
            'ignore_unauth_stats':None,
            'isolation_per_ap':None,#support new implementation of client isolation in 9.7     
            'isolation_across_ap':None,#support new implementation of client isolation in 9.7     
            'white_list':None, #support new implementation of client isolation in 9.7
            'create_guest_profile': True, #@author: liangaihua 2015-2-10 for bug ZF- 11858       
            'guest access':None, #support guest access in 9.8
            'guest_access_service': {}, # @author li.pingping 2014-05-05, to fixed bug ZF-8185
			'enable_rbac':None, #support new feature RBAC in 9.8
            'enable_dpsk':None,
            'mobile_friendly':None,
            'vlanpool':None,
            }
    conf.update(wlan_conf)

    _adapter_between_gui_and_cli(conf)
    
    _create_wlan(zdcli, conf)
    _set_newname(zdcli, conf)
    _set_ssid(zdcli, conf)

    _set_description(zdcli, conf)
    
    #zj 2014-0214  ZF-7452 fixed to adapter different parameter for 'type'
    if conf.get('type') == 'guest-access' or conf.get('type') == 'guest':
        #create default guest access
        if conf['create_guest_profile']:
            guest_access.config_guest_access(zdcli, **conf.get('guest_access_service'))
            conf['guest access'] = guest_access.default_gc_name
    if conf.get('type') == 'hotspot' and conf.get('hotspot_service'):
        hotspot.config_hotspot(zdcli, **conf.get('hotspot_service'))
        conf['hotspot_name'] = hotspot.default_hs_name
    _set_wlan_type(zdcli, conf)
    _set_encryption_type(zdcli, conf)
    _set_options(zdcli, conf)
    _set_advanced_options(zdcli, conf)



def remove_all_wlans(zdcli):
    name_list = wlangetter.get_all_wlan_name_list(zdcli)
#    for name in name_list:
#        delete_wlan(zdcli, name)
    _delete_wlans(zdcli, name_list)
    logging.info('All of WLANs have been deleted.')

def remove_wlan_config(zdcli, wlan_name):
    _remove_options(zdcli, wlan_name)
    _remove_advanced_options(zdcli, wlan_name)

def delete_wlan(zdcli, wlan_name):
    _delete_wlan(zdcli, wlan_name)

def create_multi_wlans(zdcli, wlan_conf_list):
    """
    Create a list of wlans base on the parameter
    Input: zdcli: the Zone Director CLI object
           wlan_conf_list: list of wlan configuration to be created
    """

    for wlan_conf in wlan_conf_list:
        try:
            create_wlan(zdcli, wlan_conf)

        except Exception, e:
            msg = '[Wlan %s could not be created via CLI]: %s' % (wlan_conf['name'], e)
            logging.info(msg)
            raise Exception(msg)


def _create_wlan(zdcli, conf):
    if conf['name'] is not None:
        cmd = Template(CREATE_WLAN).substitute(dict(name = conf['name'],
                                                    ))
        logging.info('Create a WLAN via ZD CLI')
        _do_excute_cmd(zdcli, cmd)

#@author:yanan.yu @since:2015-4-16 @change:adapt to 9.10 self-service guestpass
def _set_newname(zdcli,conf):
    if conf['newname'] and conf['name'] is not None:
        cmd = Template(SET_NAME).substitute(dict(name = conf['name'],newname = conf['newname']))
        logging.info('Set wlan new name [%s]' % (conf['newname'] ))
        _do_excute_cmd(zdcli, cmd)
        conf['name'] = conf['newname']
    

def _set_ssid(zdcli, conf):
    if conf['ssid'] is not None:
        ssid = conf['ssid']
        cmd = Template(SET_SSID).substitute(dict(name = conf['name'], ssid = ssid))
        logging.info('Set wlan [%s] ssid [%s]' % (conf['name'], ssid))
        _do_excute_cmd(zdcli, cmd)

def set_nas_id_type(zdcli, conf):
    if conf['nas_id_type'] is not None:
        nas_id_type = conf['nas_id_type']
        if nas_id_type == 'user-define':
            cmd = Template(SET_NAS_ID_TYPE_USER_DEF).substitute(dict(name = conf['name'], type = nas_id_type, value=conf['nas_id_value']))
        else:
            cmd = Template(SET_NAS_ID_TYPE).substitute(dict(name = conf['name'], type = nas_id_type))

        logging.info('Set wlan [%s] nasid-type [%s]' % (conf['name'], nas_id_type))
        _do_excute_cmd(zdcli, cmd)

def set_called_sta_id_type(zdcli, conf):
    if conf['called_sta_id_type'] is not None:
        cmd = Template(SET_CALLED_STA_ID_TYPE).substitute(dict(name = conf['name'], type = conf['called_sta_id_type']))

        logging.info('Set wlan [%s] called-sta-id-type [%s]' % (conf['name'], conf['called_sta_id_type']))
        _do_excute_cmd(zdcli, cmd)

def _set_description(zdcli, conf):
    if conf['description'] is not None:
        description = conf['description']
        cmd = Template(SET_DESCRIPTION).substitute(dict(name = conf['name'], description = description))
        logging.info('Set wlan [%s] description [%s]' % (conf['name'], description))
        _do_excute_cmd(zdcli, cmd)


def _set_wlan_type(zdcli, conf):
    cmd = ''
    if conf.has_key('hotspot_name'):
        hotspot_name = conf['hotspot_name']
    if conf.has_key('guest_name'):
        guest_name = conf['guest_name']
    else:
        guest_name = DEFAULT_GC_NAME
    if conf['type'] is not None:
        type = conf['type']
        if type == 'hotspot':
            cmd = Template(SET_TYPE_HOTSPOT).substitute(dict(name = conf['name'],
                                                             hotspot_name = hotspot_name
                                                              ))
        elif type == 'guest':
            cmd = Template(SET_TYPE_GUEST).substitute(dict(name = conf['name'],
                                                             guest_name = guest_name
                                                              ))
        elif type == 'autonomous':
            cmd = Template(SET_TYPE_AUTONOMOUS).substitute(dict(name = conf['name']
                                                              ))
 
        elif type.lower() == 'standard-usage':
            cmd = Template(SET_TYPE_STANDARD).substitute(dict(name = conf['name']
                                                              ))
        else:
            cmd = Template(SET_TYPE).substitute(dict(name = conf['name'],
                                                     type = type,
                                                     service = conf['guest access']
                                                     ))
    if cmd:
        logging.info('set wlan[%s] type [%s]' % (conf['name'], type))
        _do_excute_cmd(zdcli, cmd)

def _set_encryption_type(zdcli, conf):
    cmd = decide_encryption(conf)
    if cmd:
        logging.info('set wlan [%s] command is %s' % (conf['name'], cmd))
        _do_excute_cmd(zdcli, cmd)


def decide_encryption(conf):
    cmd = ''    
    if conf['encryption']:
        encryption = conf['encryption']
        #@author: Jane.Guo 2013-5-22 add to adapt upper value
        encryption = encryption.lower()

    if conf['key_string'] is not None:
        key_string = conf['key_string']

    if conf['key_index'] is not None:
        key_index = conf['key_index']

    if conf['passphrase'] is not None:
        passphrase = conf['passphrase']

    if conf['algorithm'] is not None:
        algorithm = conf['algorithm']



    if conf.has_key('auth_server'):
        if conf['auth_server']:
            auth_server = conf['auth_server']

    if conf['auth']:
        authentication = conf['auth']
        #@author: Jane.Guo 2013-5-22 add to adapt upper value
        authentication = authentication.lower()        

        if authentication in ['dot1x-eap','eap']:

            if auth_server.lower() != 'local':
                if conf['eap_type'] is not None:
                    cmd = Template(SET_DOT1X_EAP_CONF).substitute(dict(name = conf['name'],
                                                               eap_type = conf['eap_type'],
                                                               auth_server = auth_server,
                                                                ))
#                    

                    if encryption.lower() in ['wep-64', 'wep-128']:
                        cmd += Template(SET_DOT1X_WEP_CONF).substitute(dict(name = conf['name'],
                                                                           encryption = encryption,
                                                                           auth_server = auth_server,
                                                                           ))
                        return cmd
                    elif encryption.lower() in ['wpa', 'wpa2', 'wpa-mixed']:
                        cmd += Template(SET_DOT1X_WPA_CONF).substitute(dict(name = conf['name'],
                                                                           encryption = encryption,
                                                                           algorithm = algorithm,
                                                                           auth_server = auth_server,
                                                                           ))
                        return cmd
                    return cmd
                else:
                    if encryption.lower() in ['wep-64', 'wep-128']:
                        cmd = Template(SET_DOT1X_WEP_CONF).substitute(dict(name = conf['name'],
                                                                           encryption = encryption,
                                                                           auth_server = auth_server,
                                                                           ))
                        return cmd
                    elif encryption.lower() in ['wpa', 'wpa2', 'wpa-mixed']:
                        cmd = Template(SET_DOT1X_WPA_CONF).substitute(dict(name = conf['name'],
                                                                       encryption = encryption,
                                                                       algorithm = algorithm,
                                                                       auth_server = auth_server,
                                                                       ))
                        return cmd

            else:
                if conf['eap_type'] is not None:
                    cmd = Template(SET_DOT1X_EAP_CONF_LOCAL).substitute(dict(name = conf['name'],
                                                               eap_type = conf['eap_type'],
                                                                ))
                    return cmd


                elif encryption.lower() in ['wep-64', 'wep-128']:
                    cmd = Template(SET_DOT1X_WEP_CONF_LOCAL).substitute(dict(name = conf['name'],
                                                                       encryption = encryption,
                                                                       ))
                    return cmd
                elif encryption in ['wpa', 'wpa2', 'wpa-mixed']:
                    cmd = Template(SET_DOT1X_WPA_CONF_LOCAL).substitute(dict(name = conf['name'],
                                                                       encryption = encryption,
                                                                       algorithm = algorithm,
                                                                       ))
                    return cmd


        elif authentication == 'mac':
            if encryption in ['wep-64', 'wep-128']:
                cmd = Template(SET_MAC_WEP_CONF).substitute(dict(name = conf['name'],
                                                                 encryption = encryption,
                                                                 key_string = key_string,
                                                                 key_index = key_index,
                                                                 auth_server = auth_server
                                                                 ))
                return cmd

            elif encryption in ['wpa', 'wpa2', 'wpa-mixed']:
                cmd = Template(SET_MAC_WPA_CONF).substitute(dict(name = conf['name'],
                                                                 encryption = encryption,
                                                                 passphrase = passphrase,
                                                                 algorithm = algorithm,
                                                                 auth_server = auth_server
                                                                 ))
                return cmd
            else:

                cmd = Template(SET_MAC_NONE).substitute(dict(name = conf['name'],
                                                             auth_server = auth_server
                                                             ))
                return cmd

        elif authentication in ['dot1x-mac']:
            cmd = Template(SET_DOT1X_MAC_CONF).substitute(dict(name = conf['name'],
                                                       auth_server = auth_server,
                                                        ))
            return cmd

        else:
            if authentication == 'open' and encryption == 'none':
                cmd = Template(SET_OPEN_NONE).substitute(dict(name = conf['name']))
                return cmd

            if encryption in ['wep-64', 'wep-128']:
                cmd = Template(SET_WEP_CONF).substitute(dict(name = conf['name'],
                                                             authentication = authentication,
                                                             encryption = encryption,
                                                             key_string = key_string,
                                                             key_index = key_index
                                                             ))
                return cmd

            if encryption in ['wpa', 'wpa2', 'wpa-mixed']:
                cmd = Template(SET_WPA_CONF).substitute(dict(name = conf['name'],
                                                             authentication = authentication,
                                                             encryption = encryption,
                                                             passphrase = passphrase,
                                                             algorithm = algorithm
                                                             ))
                return cmd


def _set_options(zdcli, conf):
    _set_mac_addr_format(zdcli,conf)#chen.tao 2014-04-24
    _set_web_auth(zdcli, conf)
    _set_client_isolation(zdcli, conf)
    _set_zero_it(zdcli, conf)
    _set_priority(zdcli, conf)
    #@author: Jane.Guo
    _set_client_isolation_v97(zdcli, conf)
    _set_whitelist(zdcli, conf)
    _set_dpsk(zdcli,conf)

def _set_mac_addr_format(zdcli,conf):
    if not conf.get('auth').lower() == 'mac':
        return
    if conf.get('mac_addr_format') is not None:
        mac_addr_format = conf['mac_addr_format']
    else:
        mac_addr_format = "aabbccddeeff"
    cmd = Template(SET_MAC_ADDR_FORMAT).substitute({'name':conf['name'],
                                                    'mac_addr_format':mac_addr_format})
    logging.info('set wlan [%s] mac-address format as %s' % (conf['name'], mac_addr_format))
    _do_excute_cmd(zdcli, cmd)

def _remove_options(zdcli, wlan_name):
    _set_wlan_type(zdcli, dict(name = wlan_name, type = 'standard-usage'))
    _set_no_web_auth(zdcli, wlan_name)
    # for 9.7 version test, this command is not recongnize,@author: liangaihua,@change: 2015-2-6
    #_set_no_client_isolation(zdcli, wlan_name)
    _set_no_client_isolation_v97(zdcli, wlan_name)
    _set_no_zero_it(zdcli, wlan_name)

def _delete_wlans(zdcli, wlan_name_list):
    cmds = ""
    for wlan_name in wlan_name_list:
        cmd = Template(DELETE_WLAN).substitute(dict(name = wlan_name))
        cmds += cmd        
    logging.info('Delete wlans [%s]' % wlan_name_list)
    _do_excute_cmd(zdcli, cmds)

def _delete_wlan(zdcli, wlan_name):
    cmd = Template(DELETE_WLAN).substitute(dict(name = wlan_name))
    logging.info('Delete wlan [%s]' % wlan_name)
    _do_excute_cmd(zdcli, cmd)

def _set_web_auth(zdcli, conf):
    if conf['web_auth'] == True:
        if not conf['auth_server']:
            auth_server = 'local'
        else:
            auth_server = conf['auth_server']
        
        if auth_server == 'local':
            cmd = Template(SET_WEB_AUTH_LOCAL).substitute(dict(name = conf['name']))
        else:
            cmd = Template(SET_WEB_AUTH).substitute(dict(name = conf['name'],
                                                    auth_server = auth_server,
                                                    ))
        logging.info('set wlan[%s] web authentication server [%s]' % (conf['name'], auth_server))
        _do_excute_cmd(zdcli, cmd)


def _set_no_web_auth(zdcli, wlan_name):
    cmd = Template(DISABLE_WEB_AUTH).substitute(dict(name = wlan_name))
    logging.info('Set wlan[%s] disable Web authentication' % wlan_name)
    _do_excute_cmd(zdcli, cmd)

def _set_no_option82(zdcli, wlan_name):
    cmd = Template(DISABLE_OPTION82).substitute(dict(name = wlan_name))
    logging.info('Set wlan[%s] disable Option82' % wlan_name)
    _do_excute_cmd(zdcli, cmd)
    
def _set_no_force_dhcp(zdcli, wlan_name):
    cmd = Template(DISABLE_FORCE_DHCP).substitute(dict(name = wlan_name))
    logging.info('Set wlan[%s] disable Force DHCP' % wlan_name)
    _do_excute_cmd(zdcli, cmd)
    
def _set_no_fingerprinting(zdcli, wlan_name):
    cmd = Template(DISABLE_FINGERPRINTING).substitute(dict(name = wlan_name))
    logging.info('Set wlan[%s] disable Client Fingerprinting' % wlan_name)
    _do_excute_cmd(zdcli, cmd)

def _set_option82(zdcli, conf):
    if conf['option82'] is not None:
        if not conf['option82']:
            _set_no_option82(zdcli, conf['name'])
        else:    
            cmd = Template(ENABLE_OPTION82).substitute(dict(name = conf['name']))
            import random
            item1 = SUBOPTITEM1[random.randint(0,len(SUBOPTITEM1)-1)]
            item2 = SUBOPTITEM2[random.randint(0,len(SUBOPTITEM2)-1)]
            item150 = SUBOPTITEM150[random.randint(0,len(SUBOPTITEM150)-1)]
            item151 = SUBOPTITEM151[random.randint(0,len(SUBOPTITEM151)-1)]
            if conf.get('subopt1'):
                if item1 == 'disable' and item2 == 'disable' and item150 == 'disable' and item151 == 'disable':
                    item1 = SUBOPTITEM1[random.randint(0,len(SUBOPTITEM1)-2)]
                cmd += Template(SUBOPT1).substitute(dict(item = item1))
            if conf.get('subopt2'):
                cmd += Template(SUBOPT2).substitute(dict(item = item2))
            if conf.get('subopt150'):
                cmd += Template(SUBOPT150).substitute(dict(item = item150))
            if conf.get('subopt151'):
                if item151 == 'area-name':
                    item151 += ' ' + conf['name'] 
                cmd += Template(SUBOPT151).substitute(dict(item = item151))
#            cmd += "\nend"
            logging.info('Set wlan[%s] enable Option82 with CMD[%s]' % (conf['name'], cmd))
            _do_excute_cmd(zdcli, cmd)

def _set_force_dhcp(zdcli, conf):
    """
        @author: Jane.Guo
        @since: 2013-5-8
    """
    if conf['force_dhcp'] is not None:
        if not conf['force_dhcp']:
            _set_no_force_dhcp(zdcli, conf['name'])
        else:    
            cmd = Template(ENABLE_FORCE_DHCP).substitute(dict(name = conf['name']))
            logging.info('Set wlan[%s] enable force dhcp' % conf['name'])
            _do_excute_cmd(zdcli, cmd)

def _set_force_dhcp_timeout(zdcli, conf):
    """
        @author: Jane.Guo
        @since: 2013-5-8
    """
    if conf['force_dhcp_timeout'] is not None:
        cmd = Template(FORCE_DHCP_TIMEOUT).substitute(dict(name = conf['name'],
                                                           force_dhcp_timeout = conf['force_dhcp_timeout'],
                                                           ))
        logging.info('Set wlan[%s] force dhcp timeout' % conf['name'])
        _do_excute_cmd(zdcli, cmd)

def _set_fingerprinting(zdcli, conf):
    if conf['fingerprinting'] is not None:
        if not conf['fingerprinting']:
            _set_no_fingerprinting(zdcli, conf['name'])
        else:    
            cmd = Template(ENABLE_FINGERPRINTING).substitute(dict(name = conf['name']))
            logging.info('Set wlan[%s] enable Client Fingerprinting' % conf['name'])
            _do_excute_cmd(zdcli, cmd)

def _set_client_isolation(zdcli, conf):
    if conf['client_isolation'] is not None:
        isolation = conf['client_isolation']
        cmd = Template(SET_CLIENT_ISOLATION).substitute(dict(name = conf['name'],
                                                             isolation = isolation,
                                                             ))
        logging.info('set wlan[%s] client isolation [%s]' % (conf['name'], isolation))
        _do_excute_cmd(zdcli, cmd)

def _set_no_client_isolation(zdcli, wlan_name):
    cmd = Template(DISABLE_CLIENT_ISOLATION).substitute(dict(name = wlan_name))
    logging.info('Set wlan[%s] disable Client isolation' % wlan_name)
    _do_excute_cmd(zdcli, cmd)
    
def _set_client_isolation_v97(zdcli, conf):
    """
        Only support ZD version in and after 9.7
        @author: Jane.Guo
        @since: 2013-7-15
    """
    if conf.get('isolation_per_ap'):
        isolation = conf['isolation_per_ap']
        if isolation:
            isolation = ENABLE_SET
        else:
            isolation = DISABLE_SET
        cmd = Template(SET_CLIENT_ISOLATION_ON_AP).substitute(dict(name = conf['name'],
                                                             enable = isolation,
                                                             ))
        
        logging.info('set wlan[%s] client isolation [%s]' % (conf['name'], isolation))
        _do_excute_cmd(zdcli, cmd)

def _set_no_client_isolation_v97(zdcli, wlan_name):
    """
        Only support ZD version in and after 9.7
        @author: Jane.Guo
        @since: 2013-7-15
    """
    cmd = Template(SET_CLIENT_ISOLATION_ON_AP).substitute(dict(name = wlan_name,
                                                             enable = DISABLE_SET,
                                                             )) 
    logging.info('set wlan[%s] client isolation [%s]' % (wlan_name, DISABLE_SET))
    _do_excute_cmd(zdcli, cmd)

def _set_whitelist(zdcli, conf):
    """
        Only support ZD version in and after 9.7
        @author: Jane.Guo
        @since: 2013-7-15
    """
    if conf.get('isolation_across_ap'):
        white_list = conf.get('white_list')   
        cmd = Template(SET_WHITE_LIST).substitute(dict(name = conf['name'],
                                                        enable = ENABLE_SET,
                                                             white_list = white_list,
                                                             ))
        logging.info('set wlan[%s] whitelist [%s]' % (conf['name'], white_list))
        _do_excute_cmd(zdcli, cmd)

def _set_zero_it(zdcli, conf):
    if conf['zero_it']:
        cmd = Template(ENABLE_ZERO_IT).substitute(dict(name = conf['name']))
        logging.info('set zero-it [%s]' % conf['zero_it'])
        _do_excute_cmd(zdcli, cmd)
        
def _set_dpsk(zdcli, conf):
    if conf['enable_dpsk']:
        cmd = Template(ENABLE_DPSK).substitute(dict(name = conf['name']))
        _do_excute_cmd(zdcli, cmd)
    #@author: yin.wenling @since: 2014-09 adapt to 9.9 Mobile Friendly    
    if conf['mobile_friendly']:
        cmd = Template(ENABLE_MOBILE_FRIENDLY).substitute(dict(name = conf['name']))
        _do_excute_cmd(zdcli, cmd)

def _set_no_zero_it(zdcli, wlan_name):
    cmd = Template(DISABLE_ZERO_IT).substitute(dict(name = wlan_name))
    logging.info('Set wlan[%s] disable Zero IT' % wlan_name)
    _do_excute_cmd(zdcli, cmd)

def _set_priority(zdcli, conf):
    if conf['priority']:
        priority = conf['priority']
        cmd = Template(SET_PRIOTITY).substitute(dict(name = conf['name'],
                                                     priority = priority,
                                                     ))
        logging.info('set priority [%s]' % priority)
        _do_excute_cmd(zdcli, cmd)


def _set_advanced_options(zdcli, conf):
    _set_accounting(zdcli, conf)
    _set_l2acl(zdcli, conf)
    _set_l3acl(zdcli, conf)
    _set_l3acl_ipv6(zdcli, conf)
    _set_acl_dvcpcy(zdcli, conf)#chen.tao 2015-01-06, to verify vlan pool conflicts with device policy.
    _set_rate_limit(zdcli, conf)
    _set_vlan_pool(zdcli,conf)
    _set_vlan(zdcli, conf)
    _set_hide_ssid(zdcli, conf)
    _set_tunnel_mode(zdcli, conf)
    _set_proxy_arp(zdcli, conf)
    _set_background_scanning(zdcli, conf)
    _set_ignore_unauth_stats(zdcli, conf)
    _set_load_balancing(zdcli, conf)
    _set_max_client(zdcli, conf)
    _set_grace_period(zdcli, conf)
    _set_option82(zdcli, conf)
    _set_fingerprinting(zdcli, conf)
    _set_force_dhcp(zdcli, conf)
    _set_force_dhcp_timeout(zdcli, conf)
    _set_acl_dvcpcy(zdcli, conf)
    _set_rbac(zdcli,conf) #@author: Liang aihua,@since: 2015-2-3,@change: dvlan can only be enabled after rbac set
    _set_dynamic_vlan(zdcli, conf)
    _set_acl_prece(zdcli, conf)


def _remove_advanced_options(zdcli, wlan_name):
    _set_no_acct_server(zdcli, wlan_name)
    _set_no_l2acl(zdcli, wlan_name)
    _set_no_l3acl(zdcli, wlan_name)
    _set_no_vlan(zdcli, wlan_name)
    _set_no_hide_ssid(zdcli, wlan_name)
    _set_no_tunnel_mode(zdcli, wlan_name)
    _set_no_background_scanning(zdcli, wlan_name)
    _set_no_ignore_unauth_stats(zdcli, wlan_name)
    _set_no_load_balancing(zdcli, wlan_name)
    _set_no_dynamic_vlan(zdcli, wlan_name)
    _set_no_option82(zdcli, wlan_name)
    _set_no_force_dhcp(zdcli, wlan_name)


def _set_accounting(zdcli, conf):
    if conf['acc_server'] is not None:
        acct_server = conf['acc_server']

        if conf['interim'] is not None:
            interim = conf['interim']
        else:
            interim = 5
        cmd = Template(SET_ACCOUNTING).substitute(dict(name = conf['name'],
                                                   acct_server = acct_server,
                                                   interim = interim
                                                   ))
        logging.info('set accounting server: [%s]' % acct_server)
        _do_excute_cmd(zdcli, cmd)

def _set_no_acct_server(zdcli, wlan_name):
    cmd = Template(SET_NO_ACCT_SERVER).substitute(dict(name = wlan_name))
    logging.info('set no acct-server')
    _do_excute_cmd(zdcli, cmd)

def _set_l2acl(zdcli, conf):
    if conf['l2acl'] is not None:
        l2acl_name = conf['l2acl']
        cmd = Template(SET_L2ACL).substitute(dict(name = conf['name'],
                                                  l2acl_name = l2acl_name,
                                                  ))
        logging.info('set L2 ACL: [%s]' % l2acl_name)
        _do_excute_cmd(zdcli, cmd)

def _set_no_l2acl(zdcli, wlan_name):
    cmd = Template(DISABLE_L2ACL).substitute(dict(name = wlan_name))
    logging.info('Set wlan[%s] disable L2 ACL' % wlan_name)
    _do_excute_cmd(zdcli, cmd)

def _set_l3acl(zdcli, conf):
    if conf['l3acl']is not None:
        l3acl_name = conf['l3acl']
        cmd = Template(SET_L3ACL).substitute(dict(name = conf['name'],
                                                  l3acl_name = l3acl_name,
                                                  ))
        logging.info('set L3 ACL: [%s]' % l3acl_name)
        _do_excute_cmd(zdcli, cmd)
        
def _set_l3acl_ipv6(zdcli, conf):
    if conf['l3acl_ipv6']is not None:
        l3acl_name = conf['l3acl_ipv6']
        cmd = Template(SET_L3ACL_IPV6).substitute(dict(name = conf['name'],
                                                       l3acl_ipv6_name = l3acl_name,
                                                       ))
        logging.info('set L3 IPV6 ACL: [%s]' % l3acl_name)
        _do_excute_cmd(zdcli, cmd)


def _set_no_l3acl(zdcli, wlan_name):
    cmd = Template(DISABLE_L3ACL).substitute(dict(name = wlan_name))
    logging.info('Set wlan[%s] disable L3 ACL' % wlan_name)
    _do_excute_cmd(zdcli, cmd)


def _set_rate_limit(zdcli, conf):
    if conf['rate_limit_uplink']:
        rate_limit_uplink = conf['rate_limit_uplink']
        rate_limit_downlink = conf['rate_limit_downlink']

        cmd = Template(SET_RATE_LIMIT).substitute(dict(name = conf['name'],
                                                       rate_limit_uplink = rate_limit_uplink,
                                                       rate_limit_downlink = rate_limit_downlink,
                                                       ))
        logging.info('set rate limit:[%s] X [%s]' % (rate_limit_uplink, rate_limit_downlink))
        _do_excute_cmd(zdcli, cmd)

def _set_rbac(zdcli,conf):
    if conf['enable_rbac']:
        enable_rbac = conf['enable_rbac']
        cmd = Template(ENABLE_RBAC).substitute(
                                               dict(name = conf['name'],
                                                    enable_rbac = enable_rbac,
                                                    )
                                               )
        logging.info('set Role-Base Access Control %s' % enable_rbac)
        _do_excute_cmd(zdcli, cmd)

def _set_vlan_pool(zdcli,conf):
    cmd = ''
    if conf['vlanpool']:
        vlan_pool_name = conf['vlanpool']
        cmd += Template(ENABLE_VLAN_POOL).substitute(
                                               dict(name = conf['name'],
                                                    vlan_pool_name = vlan_pool_name,
                                                    )
                                               )
        logging.info('set vlan pool %s enabled' % vlan_pool_name)
     
        if conf['dvlan']:
            cmd += ENABLE_DVLAN_COMMAND
            logging.info('Set dynamic Vlan')
    if cmd:
        _do_excute_cmd(zdcli, cmd)

def _set_vlan(zdcli, conf):
    # feature update for 9.4   
    if conf['vlan_id']is not None:
        if conf['vlan_id']:
            vlan_id = conf['vlan_id']
        else:
            #If no need for vlan id, set to default value 1.
            vlan_id = 1 
        cmd = Template(SET_VLAN).substitute(dict(name = conf['name'],
                                                 vlan_id = vlan_id,))
        logging.info('set vlan id: [%s]' % str(vlan_id))
        _do_excute_cmd(zdcli, cmd)

def _set_no_vlan(zdcli, wlan_name):
    cmd = Template(DISABLE_VLAN).substitute(dict(name = wlan_name))
    logging.info('Set wlan[%s] disable Vlan' % wlan_name)
    _do_excute_cmd(zdcli, cmd)

def _set_hide_ssid(zdcli, conf):
    if conf['hide_ssid']:
        cmd = Template(ENABLE_HIDE_SSID).substitute(dict(name = conf['name']))
        logging.info('set hide ssid')
        _do_excute_cmd(zdcli, cmd)


def _set_no_hide_ssid(zdcli, wlan_name):
    cmd = Template(DISABLE_HIDE_SSID).substitute(dict(name = wlan_name))
    logging.info('Set wlan[%s] disable hide ssid' % wlan_name)
    _do_excute_cmd(zdcli, cmd)

def _set_tunnel_mode(zdcli, conf):
    if conf['tunnel_mode'] is not None:
        if conf['tunnel_mode']:
            cmd = Template(ENABLE_TUNNEL_MODE).substitute(dict(name = conf['name']))
            logging.info('set tunnel mode enable')
            _do_excute_cmd(zdcli, cmd)
        else:
            cmd = Template(DISABLE_TUNNEL_MODE).substitute(dict(name = conf['name']))
            logging.info('set tunnel mode disable')
            _do_excute_cmd(zdcli, cmd)

def _set_no_tunnel_mode(zdcli, wlan_name):
    cmd = Template(DISABLE_TUNNEL_MODE).substitute(dict(name = wlan_name))
    logging.info('Set wlan[%s] disable Tunnel mode' % wlan_name)
    _do_excute_cmd(zdcli, cmd)

def _set_proxy_arp(zdcli, conf):
    if conf['do_proxy_arp'] is not None:
        if conf['do_proxy_arp']:
            cmd = Template(ENABLE_PROXY_ARP).substitute(dict(name = conf['name']))
            logging.info('set proxy arp enable')
            _do_excute_cmd(zdcli, cmd)
        else:
            cmd = Template(DISABLE_PROXY_ARP).substitute(dict(name = conf['name']))
            logging.info('set proxy arp disable')
            _do_excute_cmd(zdcli, cmd)

def _set_background_scanning(zdcli, conf):
    if conf['bgscan'] == True:
        cmd = Template(ENABLE_BGSCAN).substitute(dict(name = conf['name']))
        logging.info('Set background scan')
        _do_excute_cmd(zdcli, cmd)
    elif conf['bgscan'] == False:
        _set_no_background_scanning(zdcli, conf['name'])

def _set_no_background_scanning(zdcli, wlan_name):
    cmd = Template(DISABLE_BGSCAN).substitute(dict(name = wlan_name))
    logging.info('Set wlan[%s] disable background scanning' % wlan_name)
    _do_excute_cmd(zdcli, cmd)

def _set_ignore_unauth_stats(zdcli, conf):
    if conf.get('ignore_unauth_stats') is not None:      
        if conf.get('ignore_unauth_stats'):
            cmd = Template(ENABLE_IGNORE_UNAUTH_STATS).substitute(dict(name = conf['name']))
            logging.info('Set WLAN[%s] enable ignore unauth stats' % conf['name'])
            _do_excute_cmd(zdcli, cmd)
        else:
            _set_no_ignore_unauth_stats(zdcli, conf['name'])
    
def _set_no_ignore_unauth_stats(zdcli, wlan_name):
    cmd = Template(DISABLE_IGNORE_UNAUTH_STATS).substitute(dict(name=wlan_name))
    _do_excute_cmd(zdcli, cmd)
    logging.info('Set WLAN %s disable ignore unauth stats' % wlan_name)

def _set_load_balancing(zdcli, conf):
    if conf['load_balance']:
        cmd = Template(ENABLE_LOAD_BALANCING).substitute(dict(name = conf['name']))
        logging.info('Set load balancing')
        _do_excute_cmd(zdcli, cmd)

def _set_no_load_balancing(zdcli, wlan_name):
    cmd = Template(DISABLE_LOAD_BALANCING).substitute(dict(name = wlan_name))
    logging.info('Set wlan[%s] disable load balancing' % wlan_name)
    _do_excute_cmd(zdcli, cmd)

def _set_max_client(zdcli, conf):
    if conf['max_clients']:
        max_client = conf['max_clients']
        cmd = Template(SET_MAX_CLIENT).substitute(dict(name = conf['name'],
                                                           max_client = max_client,
                                                           ))
        logging.info('Set Max client: [%s]' % str(max_client))
        _do_excute_cmd(zdcli, cmd)

def _set_dynamic_vlan(zdcli, conf):
    if conf['dvlan']:
        cmd = Template(ENABLE_DYNAMIC_VLAN).substitute(dict(name = conf['name']))
        logging.info('Set dynamic Vlan')
        _do_excute_cmd(zdcli, cmd)

def _set_no_dynamic_vlan(zdcli, wlan_name):
    cmd = Template(DISABLE_DYNAMIC_VLAN).substitute(dict(name = wlan_name))
    logging.info('Set wlan[%s] disable dynamic vlan' % wlan_name)
    _do_excute_cmd(zdcli, cmd)

def _set_grace_period(zdcli, conf):
    if conf['type'] == 'hotspot':
        logging.info('wlan type is hotspot, configuring grace period is forbidden.')
        return        

    elif conf['type'] == 'autonomous':
        logging.info('wlan type is autonomous, configuring grace period is forbidden.')
        return 
    
    elif conf['type'] == 'social-media':
        logging.info('wlan type is social-media, configuring grace period is forbidden.')
        return 
    elif conf['type'] == 'social-media':
        logging.info('wlan type is social-media, configuring grace period is forbidden.')
        return
    elif 'standard' in conf['type'].lower():
        if not conf['web_auth'] or not conf.get('do_webauth'):
            if conf['grace_period']:
                logging.info('wlan type is standard and webauth is disabled, configuring grace period is forbidden.')
                return  
    wlan_name = conf['name']
    grace_period = conf['grace_period']
    
    if conf['grace_period'] == None:#@author: anzuo @change: 9.9 grace period is enabled by default when create wlan
        cmd = Template(DISABLE_GRACE_PERIOD).substitute(dict(name = wlan_name))
        logging.info("Disable grace period in wlan[%s]" % wlan_name)
        _do_excute_cmd(zdcli, cmd)
        return
    
    if conf['grace_period'] == False:
        cmd = Template(DISABLE_GRACE_PERIOD).substitute(dict(name = wlan_name))
        logging.info("Disable grace period in wlan[%s]" % wlan_name)
        
    else:
        cmd = Template(SET_GRACE_PERIOD).substitute(dict(name = wlan_name, 
                                                         grace_period = grace_period))
        logging.info("Set grace period to '%s' in wlan[%s]" % (grace_period, wlan_name))
        
    _do_excute_cmd(zdcli, cmd)

def _set_acl_dvcpcy(zdcli, conf):
    """
    This function support to set the device policy name to WLAN
    @author: An Nguyen, Jun 2013
    """
    wlan_name = conf['name']
    if conf.get('dvcpcy_name') == None:
    #@author: Anzuo, @change: the get method of dict will never return "false", so script cannot del device policy
#        return
#    elif conf.get('dvcpcy_name') == False:
        if conf['dvlan']:
            cmd = Template(DISABLE_DEVICE_POLICY_ONLY).substitute(dict(name=wlan_name))
        else:
            cmd = Template(DISABLE_DEVICE_POLICY).substitute(dict(name=wlan_name))
        logging.info('Disable Device Policy in WLAN[%s]' % wlan_name)
    elif conf.get('dvcpcy_name') != None:
        cmd = Template(ENABLE_DEVICE_POLICY).substitute(dict(name=wlan_name,
                                                             dvcpcy_name = conf.get('dvcpcy_name')))
        logging.info('Set device policy "%s" to WLAN[%s]' % (conf.get('dvcpcy_name'), wlan_name))
    
    _do_excute_cmd(zdcli, cmd)

def _set_acl_prece(zdcli, conf):
    """
    This function support to set the precedence policy name to WLAN
    @author: An Nguyen, Jun 2013
    """
    wlan_name = conf['name']
    
    if conf.get('prece_name') == None:
        return
    
    cmd = Template(ENABLE_PRECEDENCE_POLICY).substitute(dict(name=wlan_name,
                                                             prece_name = conf.get('prece_name')))
    logging.info('Set precedence policy "%s" to WLAN[%s]' % (conf.get('prece_name'), wlan_name))
    
    _do_excute_cmd(zdcli, cmd)

def _do_excute_cmd(zdcli, cmd, timeout = 40):
    try:
        #chen.tao 2015-01-06, to find out errors which occured during wlan configurations
        #for example, when an incorrect command is executed, an error info shows, then execute 'exit'
        #the error would be ignored in the past, now raise exception if error occurs.
        raw_cmd = cmd.strip()
        target_cmd = raw_cmd.split('\n')[-1]
        cmd = cmd + SAVE_SERVER_CONFIG
        time.sleep(1)
        logging.info("CLI is: %s" % cmd)
        res = zdcli.do_cfg(cmd, timeout = timeout, raw = True)
        time.sleep(2)

        if res.has_key('exit') and "Your changes have been saved." not in res['exit'][0]:
            zdcli.back_to_priv_exec_mode(back_cmd = 'quit', print_out = True)
            raise Exception("Wlan configuration is not saved successfully. Result is %s" % res)
        if 'wlan ' in target_cmd or 'no wlan' in target_cmd or ' wlan ' in target_cmd:
            return	
			
        #ZF-11980 20150211
		#Anzuo, 2015-1-30, update due to prompt message behavior change to wlan configuration via CLI
        if target_cmd and res.has_key(target_cmd) and ("The command was executed successfully" not in res[target_cmd][0] \
             and "has been updated and saved" not in res[target_cmd][0]):
            raise Exception("Error was found:%s" % res[target_cmd][0])
#        if target_cmd and res.has_key(target_cmd) and ("The command was executed successfully" not in res[target_cmd][0] :
            raise Exception("Error was found:%s" % res[target_cmd][0])
   		#Anzuo, 2015-1-30, update due to prompt message behavior change to wlan configuration via CLI
    except Exception, ex:
        errmsg = ex.message
        raise Exception(errmsg)

def verify_wlan_all_between_set_and_get(set_conf_list, get_info_dict):
    """
    set_conf_list: 
    [ {name:'',...},
    {name:'',...}
    ]
    
    get_info_dict:
    {'1': {   'Accounting Server': 'Disabled',
             'Authentication': 'open',
             'Authentication Server': 'Disabled',
             'Background Scanning': 'Enabled',
             'Client Isolation': 'None',},
    '10': {   'Accounting Server': 'Disabled',
              'Authentication': 'open',
              'Authentication Server': 'Disabled',
              'Background Scanning': 'Enabled',
    
    """
    get_info_list = get_info_dict.values()

    set_conf_len = len(set_conf_list)
    get_info_len = len(get_info_list)
    if set_conf_len != get_info_len:
        return('FAIL,The number of wlans in CLI [%d] is not the same as in GUI [%d]' % (set_conf_len, get_info_len))

    for i in range(set_conf_len):
        for j in range(get_info_len):
            if set_conf_list[i]['name'] == get_info_list[j]['NAME']:
                res = _verify_wlan_between_set_and_get(set_conf_list[i], get_info_list[j])
                if res:
                    return res
                else:
                    logging.debug('set conf is %s, get info is %s' % (set_conf_list[i], get_info_list[j]))
                    break
            elif j == get_info_len - 1:
                return('The wlan [%s] exists in Set configuration, but can NOT get it' % set_conf_list[i]['NAME'])

    logging.info('All wlan information in CLI is correct')

def set_max_client(zdcli, wlan_name,number):
    conf={
          'name':wlan_name,
          'max_clients':number
          }
    _set_max_client(zdcli, conf)

def verify_wlan_between_cli_set_and_gui_get(cli_set_list, gui_get_dict):
    '''
    cli_set_list:
        set_conf_list: 
        [ {name:'',...},
        {name:'',...}
        ]
    gui_get_dict:
        $name:{
        name:'',..
        }
        ...
    '''
    found = False
    gui_wlan_name_list = gui_get_dict.keys()
    for wlan_conf in cli_set_list:
        for gui_wlan_name in gui_wlan_name_list:
            if wlan_conf['name'] == gui_wlan_name:
                found = True
                res = _verify_wlan_between_cli_set_and_gui_get(wlan_conf, gui_get_dict[gui_wlan_name])
                if res:
                    logging.info("CLI Set is %s\n GUI Get is %s" % (wlan_conf, gui_get_dict[gui_wlan_name]))
                    return res

                else:
                    break

    if not found:
        logging.info("There is not Wlan on WEBUI match the WLAN CLI config")
        return ("There is not Wlan on WEBUI match the WLAN CLI config")


def _verify_wlan_between_set_and_get(cli_set, cli_get):
    logging.info('Verify Set configuration and show inforation are the same')
    key_map_dict = {
                    'name':'NAME',
                    'ssid':'SSID',
                    'description':'Description',
                    'type':'Type',
                    'auth':'Authentication',
                    'encryption':'Encryption',
                    'algorithm':'Algorithm',
                    'passphrase':'Passphrase',
                    'web_auth':'Web Authentication',
                    'auth_server':'Authentication Server',
                    'tunnel_mode':'Tunnel Mode',
                    'bgscan':'Background Scanning',
                    'max_clients':'Max. Clients',
#                    'client_isolation':'Client Isolation',
                    'zero_it':'Zero-IT Activation',
                    'priority':'Priority',
                    'load_balance':'Load Balancing',
                    'eap_type':'EAP TYPE',
                    'rate_limit_uplink':'Rate Limiting Uplink',
                    'rate_limit_downlink':'Rate Limiting Downlink',
                    'dvlan':'Dynamic VLAN',
                    'hide_ssid':'Closed System',
#                    'l2acl':'L2/MAC',
                    'l3acl':'L3/L4/IP Address',
                    'vlan':'VLAN-ID',
                    }

    result = {}
    for key in cli_set.keys():
        for k, v in key_map_dict.items():
            if k == key:
                result[k] = cli_get[v]

    for key in result.keys():
        if result[key] == ['Enabled', 'Enabled'] or result[key] == 'Enabled':
            result[key] = True
        elif result[key] == ['Disabled', 'Diabled'] or result[key] == 'Disabled':
            result[key] = False

        if str(result[key]).lower() == 'wep64':
            result[key] = 'wep-64'

        if str(result[key]).lower() == 'wep128':
            result[key] = 'wep-128'

        if str(result[key]).lower() == 'mac-auth':
            result[key] = 'mac'

        if str(result[key]).lower() == '802.1x-eap':
            result[key] = 'dot1x-eap'

        if str(result[key]).lower() == 'local database':
            result[key] = 'local'

        if str(result[key]).lower() == 'standard usage':
            result[key] = 'standard-usage'

        if str(result[key]).lower() == 'guest access':
            result[key] = 'guest-access'

        if result[key] == 'Hotspot Service(WISPr)':
            result[key] = 'hotspot'

        if str(cli_set[key]).lower() not in str(result[key]).lower():
            return ('CLI Get info [%s] is: %s\n, CLI set info is: %s \n' % (key, result[key], cli_set[key]))

    if cli_set.has_key('grace_period'):
        if cli_set['grace_period'] == False:
            if cli_get['Grace Period']['Status'] != 'Disabled':
                return ('Grace Period info in CLI is: %s\n, set info is: %s\n' % (cli_get['Grace Period'], cli_set['grace_period']))
        
        elif cli_set['grace_period']:
            if cli_get['Grace Period']['Status'] != 'Enabled' \
            or cli_get['Grace Period']['Period'] != '%s Minutes' % cli_set['grace_period']:
                return ('Grace Period info in CLI is: %s\n, set info is: %s\n' % (cli_get['Grace Period'], cli_set['grace_period']))

def _verify_wlan_between_cli_set_and_gui_get(cli_set, gui_get):
    '''
    gui_get:
    {'name':'',
     ...,
     'algorithm': 'auto',
     'zero_it': 'Disabled'
     }
    
    cli_set:
     {name:'',...}
    '''
    logging.info("Verify wlan between CLI Set and GUI Get")
    set_key_list = cli_set.keys()
    for key in set_key_list:
        if gui_get.has_key(key):
            if gui_get[key] == 'Local Database':
                gui_get[key] = 'local'

            if gui_get[key] == 'Enabled':
                gui_get[key] = True

            if gui_get[key] == 'Disabled':
                gui_get[key] = False

            if str(cli_set[key]).lower() not in str(gui_get[key]).lower():
                logging.info('%s:cli set [%s] does not equal to gui get [%s]' % (key, cli_set[key], gui_get[key]))
                return ("%s:CLI Set is: [%s], GUI Get is %s" % (key, cli_set[key], gui_get[key]))
#    return True

def _verify_wlan_after_remove_cfg(cli_get):
    """
      cli_get:
      NAME= test
      SSID= test
      Description=
      Type= Standard Usage
      Authentication= open
      Encryption= none
      Web Authentication= Disabled
      Authentication Server= Disabled
      Accounting Server= Disabled
      Tunnel Mode= Disabled
      Background Scanning= Enabled
      Max Clients= 100
      Client Isolation= None
      Zero-IT Activation= Disabled
      Priority= High
      Load Balancing= Disabled
      Rate Limiting Uplink= Disabled
      Rate Limiting Downlink= Disabled
      VLAN= Disabled
      Dynamic VLAN= Disabled
      Closed System= Disabled
      ofdm-only State= Disabled
      PMK Cache Time= 720 minutes
      NAS-ID Type= wlan-bssid
      L3/L4/IP Address= No ACLS
"""

    if cli_get.has_key('Accounting Server'):
        if cli_get['Accounting Server'].lower() != 'disabled':
            return ("FAIL, Accounting Server is not Disabled --incorrect behaver")

    if cli_get['Web Authentication'].lower() != 'disabled':
        return('Web Authentication is not disabled --incorrect behaver')

    try:
        if cli_get['Client Isolation'].lower() != 'none':
            return('Client Isolation is not None -- incorrect behaver')
    except:
        pass

    if cli_get['Zero-IT Activation'].lower() != 'disabled':
        return('Zero-IT Activation is not Disabled--incorrect behaver')

    if cli_get['L2/MAC'].upper() != 'NO ACLS':
        return('There is L2 ACL -- incorrect behaver')

    if cli_get['L3/L4/IP Address'].upper() != 'NO ACLS':
        return('There is L3 ACL -- incorrect behaver')

    try:
        if cli_get['VLAN'].lower() != 'disabled' or str(cli_get['VLAN-ID'].lower()) != u'1':
            return('VLAN is not disabled -- incorrect behaver')
    except:
        if str(cli_get['VLAN-ID']) != u'1':
            return('VLAN-ID is not disabled -- incorrect behaver')

    if cli_get['Closed System'].lower() != 'disabled':
        return('Hide SSID(Closed System) is not disabled -- incorrect behaver')

    if cli_get['Tunnel Mode'].lower() != 'disabled':
        return('Tunnel Mode is not disabled -- incorrect behaver')

    if cli_get['Background Scanning'].lower() != 'disabled':
        return('Background Scanning is not disabled -- incorrect behaver')

#    if cli_get['Load Balancing'].lower() != 'disabled':
#        return('Load Balancing is not disabled -- incorrect behaver')

    if cli_get['Dynamic VLAN'].lower() != 'disabled':
        return('Dynamic VLAN is not disabled -- incorrect behaver')
