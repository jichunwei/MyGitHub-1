'''
Config AP policy

'''

import time
import logging
from string import Template
from RuckusAutoTest.components.lib.zdcli import output_as_dict as output

SET_AP_MGMT_VLAN = '''
ap-policy
    ap-management-vlan $vlan_id
'''    

REMOVE_AP_MGMT_VLAN = '''
ap-policy
    no ap-management-vlan
'''

SET_AP_AUTO_APPROVE = '''
config
ap-policy
    ap-auto-approve 
exit
'''

REMOVE_AP_AUTO_APPROVE = '''
config
ap-policy
    no ap-auto-approve
exit
'''

SET_AP_MAX_CLIENTS = '''
ap-policy
    ap-max-clients $client_no
'''

SET_AP_INTERNAL_HEATER = '''
ap-policy
    ap-internal-heater
'''

REMOVE_AP_INTERNAL_HEATER  = '''
ap-policy
    no ap-internal-heater
'''

SET_AP_RADIO_TX = '''
ap-policy
    ap-radio &radion tx-power $power
'''

SET_AP_RADIO_11N = '''
ap-policy
    ap-radio $radion 11n-only $n_mode
'''

SET_POE_PORT = '''
ap-policy
    ap-poe-port 
'''

REMOVE_POE_PORT = '''
ap-policy
    no ap-poe-port
'''

SET_AP_MODEL = '''
ap-policy
    ap-model $model
'''

SET_LIMITED_ZD_DISCOVERY = '''
ap-policy
    limited-zd-discovery zd-ip $pri_zd_ip $sec_zd_ip
'''

REMOVE_LIMITED_ZD_DISCOVERY = '''
ap-policy
 no limited-zd-discovery
'''

SET_LED = '''
ap-policy
    led $led_model
'''

REMOVE_LED = '''
ap-policy
    no led $led_model
'''

GET_AP_POLICY = '''
ap-policy
    show
'''

#Add command defination for limited zd discovery.
ENTER_AP_POLICY = "ap-policy"
SET_LIMITED_ZD_DISCOVERY_IP = "limited-zd-discovery zd-ip $pri_zd_ip $sec_zd_ip"
SET_LIMITED_ZD_DISCOVERY_DNS = "limited-zd-discovery zd-addr '$pri_zd_ip' '$sec_zd_ip'"
ENABLE_LIMITED_ZD_DISCOVERY_KEEP_AP_SETTING = "limited-zd-discovery keep-ap-setting"
DISABLE_LIMITED_ZD_DISCOVERY_KEEP_AP_SETTING = "no limited-zd-discovery keep-ap-setting"
ENABLE_LIMITED_ZD_DISCOVERY_PREFER_PRIMARY_ZD = "limited-zd-discovery prefer-primary-zd"
DISABLE_LIMITED_ZD_DISCOVERY_PREFER_PRIMARY_ZD = "no limited-zd-discovery prefer-primary-zd"
DISABLE_LIMITED_ZD_DISCOVERY = "no limited-zd-discovery"

def set_ap_polic(zdcli,conf):
    '''
    conf = {'vlan_id':1/2/3/302/.../keeping
            'auto_approve':True/False/None
            }
    '''
    cmd = '''ap-policy'''

    if conf.has_key('vlan_id') and conf['vlan_id']:
        if not conf['vlan_id']=='keeping':
            cmd += '\nap-management-vlan ap-management-vlan %s' %(conf['vlan_id'])
        else:
            cmd += '\nap-management-vlan %s' %(conf['vlan_id'])
    
    if conf.has_key('auto_approve') and conf['auto_approve'] is not None:
        if conf['auto_approve']:
            cmd += '\nap-auto-approve'
        else:
            cmd += '\nno ap-auto-approve'
    
    if conf.get('client_no'):
        cmd += '\nap-max-clients %s' %(conf['client_no'])
    
    if conf.get('internal_heater'):
        cmd += '\nap-internal-heater'
    
    if conf.get('radio'):
        radio = conf['radio']
    
        if conf['power']:
            power = conf['power']
            cmd += '\nap-radio %s tx-power %s' %(radio, power)
    
        if conf['n_mode']:
            n_mode = conf['n_mode']
            cmd += '\nap-radio %s 11n-only %s' (radio, n_mode)

    if conf.get('poe_port'):
        cmd += '\nap-poe-port'
         
    if conf.get('model'):
        cmd += '\nap-model %s' %(conf['model'])
        
    if conf.get('pri_zd_ip'):
        pri_zd_ip = conf['pri_zd_ip']
        if conf.has_key('sec_zd_ip'):
            sec_zd_ip = conf['sec_zd_ip']
        else:
            sec_zd_ip = ''
        
        cmd += '\nlimited-zd-discovery zd-ip %s %s' % (pri_zd_ip,sec_zd_ip)

    if conf.has_key('led_conf'):
        led_conf = conf['led_conf']
        if led_conf['led']:
            cmd += '\nled %s' % conf['led_model']
        
        else:
            cmd += '\n no led %s' %conf['led_model']
        
    _do_excute_cmd(zdcli,cmd)

def cfg_limited_zd_discovery(zdcli, zd_discover_cfg):
    '''
    Configure limited zd discovery.
    
    Input:
       keep_ap_setting: set it is as True if want to keep ap setting.
       is_dns: set it is as True if one of primary and secondary is domain name;
               set as False if both or primary and secondary is ip address.  
       zd_discover_cfg:
       {enabled = True,        
        primary_zd_ip = '192.168.0.2',
        secondary_zd_ip = '192.168.0.3',
        keep_ap_setting = False,
        prefer_prim_zd = False,
        }
        
    Output: 
       result: True if command is executed successfully; False if any error message.
       err_list: string, error message information.
    '''
    limited_zd_cfg = dict(enabled = True,
                          primary_zd_ip = '192.168.0.2',
                          secondary_zd_ip = '192.168.0.3',
                          keep_ap_setting = False,
                          prefer_prim_zd = False,)
    
    limited_zd_cfg.update(zd_discover_cfg)
    
    cmd_block = _construct_cmd_block_limited_zd(limited_zd_cfg)
    
    res = _do_excute_cmd(zdcli,cmd_block)    
    err_list = _parse_res(res)
    
    return err_list

def get_limited_zd_discovery(zdcli):
    '''
    CLI ZD discovery original settings:
    Limited ZD Discovery:
    
    Status= Disabled
    
    Status= Enabled
    Keep AP's ZoneDirector Settings = true
    
    Status= Enabled
    Primary ZoneDirector ADDR= www.ruckuszd1.net
    Secondary  ZoneDirector ADDR= 192.168.0.2
    Prefer Primary ZoneDirector = true
    
    Output:
        {enabled = True,
        primary_zd_ip = '192.168.0.2',
        secondary_zd_ip = '192.168.0.3',
        keep_ap_setting = False,
        prefer_prim_zd = False,
        }
    '''
    ap_policy_cfg = get_ap_policy(zdcli)
    
    limited_zd_key = 'Limited ZD Discovery'
    
    ret_limited_zd_cfg = {}
    
    if ap_policy_cfg.has_key(limited_zd_key):
        limited_zd_cfg = ap_policy_cfg[limited_zd_key]
        
        status = limited_zd_cfg.get('Status')
        if status.lower() == 'enabled':
            ret_limited_zd_cfg['enabled'] = True
            keep_ap_setting = limited_zd_cfg.get("Keep AP's ZoneDirector Settings")
            if keep_ap_setting and keep_ap_setting.lower() == 'true':
                ret_limited_zd_cfg['keep_ap_setting'] = True
            else:
                ret_limited_zd_cfg['keep_ap_setting'] = False
                
                primary_zd_ip = limited_zd_cfg.get('Primary ZoneDirector ADDR')
                secondary_zd_ip = limited_zd_cfg.get('Secondary  ZoneDirector ADDR')
                prefer_prim_zd = limited_zd_cfg.get('Prefer Primary ZoneDirector')
                
                ret_limited_zd_cfg['primary_zd_ip'] = primary_zd_ip
                ret_limited_zd_cfg['secondary_zd_ip'] = secondary_zd_ip
                if prefer_prim_zd and prefer_prim_zd.lower() == 'true':
                    ret_limited_zd_cfg['prefer_prim_zd'] = True
                else:
                    ret_limited_zd_cfg['prefer_prim_zd'] = False
        else:
            ret_limited_zd_cfg['enabled'] = False
            
    return ret_limited_zd_cfg

def verify_limited_zd_discovery(dict_1, dict_2):
    '''
    Verify two limited ZD discovery cfg dict are same.
    '''
    status_1 = dict_1['enabled']
    status_2 = dict_2['enabled']
    
    err_msg = ''
    if status_1 != status_2:        
        err_msg = 'Status is different: %s, %s' % (status_1, status_2)
    else:
        if status_1 == True:
            keep_ap_setting_1 = dict_1.get('keep_ap_setting')
            keep_ap_setting_2 = dict_2.get('keep_ap_setting')
            if keep_ap_setting_1 != keep_ap_setting_2:
                err_msg = 'Keep AP setting are different: %s, %s' % (keep_ap_setting_1, keep_ap_setting_2)
            else:
                if keep_ap_setting_1 == False:
                    if dict_1.get('primary_zd_ip') != dict_2.get('primary_zd_ip'):
                        err_msg = "Primary ZD IP/ADDR are different: %s, %s" % (dict_1['primary_zd_ip'], dict_2['primary_zd_ip'])
                    if dict_1.get('secondary_zd_ip') != dict_2.get('secondary_zd_ip'):
                        err_msg = "Secondary ZD IP/ADDR are different: %s, %s" % (dict_1['secondary_zd_ip'], dict_2['secondary_zd_ip'])
                    if dict_1.get('prefer_prim_zd') != dict_2.get('prefer_prim_zd'):
                        err_msg = "Perfer primary ZD are different: %s, %s" % (dict_1['prefer_prim_zd'], dict_2['prefer_prim_zd'])
    return err_msg

def _construct_cmd_block_limited_zd(limited_cfg):
    '''
    Set limited zd discovery.
    If keep_ap_setting is True, set limited zd discovery as keep-ap-setting.
    Else, set primary and secondary ip/dns values.
    '''
    cmd_block = "%s\n" % ENTER_AP_POLICY
    if limited_cfg['enabled'] == True:
        if limited_cfg['keep_ap_setting'] == True:
            cmd_block += "%s\n" % ENABLE_LIMITED_ZD_DISCOVERY_KEEP_AP_SETTING
        else:
            cmd_block += "%s\n" % DISABLE_LIMITED_ZD_DISCOVERY_KEEP_AP_SETTING
            
            if limited_cfg['prefer_prim_zd'] == True:
                cmd_block += "%s\n" % ENABLE_LIMITED_ZD_DISCOVERY_PREFER_PRIMARY_ZD
            else:
                cmd_block += "%s\n" % DISABLE_LIMITED_ZD_DISCOVERY_PREFER_PRIMARY_ZD
                
            primary_zd_ip = limited_cfg['primary_zd_ip']
            secondary_zd_ip = limited_cfg['secondary_zd_ip']
            
            if not primary_zd_ip:
                primary_zd_ip = ""
            if not secondary_zd_ip:
                secondary_zd_ip = ""
                
            cmd_block += Template(SET_LIMITED_ZD_DISCOVERY_DNS).substitute(dict(pri_zd_ip = primary_zd_ip, sec_zd_ip=secondary_zd_ip))
            #cmd_block += Template(SET_LIMITED_ZD_DISCOVERY_IP).substitute(dict(pri_zd_ip = primary_zd_ip, sec_zd_ip=secondary_zd_ip))
    else:
        cmd_block += "%s\n" % DISABLE_LIMITED_ZD_DISCOVERY
        
    return cmd_block

def _parse_res(res):
    '''
    Parsing result of executing command.
    #ruckus(config-ap-policy)# limited-zd-discovery zd-addr www.ipv4-ruckuszd1-max-length-ruckusruckusruckusruckusruckus.net1234
    #The Primary ZoneDirector IP/IPv6 address or FQDN can not be empty or longer than 64 bytes.
    #The secondary ZoneDirector IP/IPv6 address or FQDN can not be longer than 64 bytes.
    res is a dict, key is the command executed, value is the response message.
    '''
    err_list = []
    err_msg_list = ['invalid', 'fail', 'error', 'sorry', 'can not be']
    if res and type(res) == dict:
        for cmd, res_list in res.items():
            res_str = str(res_list)
            for err_msg in err_msg_list:
                if err_msg in res_str.lower():
                    err_list.append("Cmd=%s, Error=%s" % (cmd, res_str))
    else:
        err_list.append(res)
                                        
    return err_list
    
def _set_ap_mgmt_vlan(zdcli,conf):
    if conf['vlan_id']:
        cmd = Template(SET_AP_MGMT_VLAN).substitute(dict(vlan_id = conf['vlan_id']))
        _do_excute_cmd(zdcli,cmd)


def _remove_ap_mgmt_vlan(zdcli):
    cmd = REMOVE_AP_MGMT_VLAN
    _do_excute_cmd(zdcli,cmd)


def _set_ap_auto_approve(zdcli,conf):
    if conf['auto_approve']:
        cmd = SET_AP_AUTO_APPROVE
        _do_excute_cmd(zdcli,cmd)

         
def _remove_ap_auto_approve(zdcli):
    cmd = REMOVE_AP_AUTO_APPROVE
    _do_excute_cmd(zdcli,cmd)
    

def _set_ap_max_clients(zdcli,conf):
    if conf['client_no']:
        cmd = Template(SET_AP_MAX_CLIENTS).substitute(dict(client_no = conf['client_no']))
        _do_excute_cmd(zdcli,cmd)
    

def _set_ap_internal_heater(zdcli,conf):
    if conf['internal_heater']:
        cmd = SET_AP_INTERNAL_HEATER 
        _do_excute_cmd(zdcli,cmd)

        
def _remove_ap_internal_heater(zdcli):
    cmd = REMOVE_AP_INTERNAL_HEATER
    _do_excute_cmd(zdcli,cmd)

    
def _set_ap_radio_tx(zdcli,conf):
    if conf['radio']:
        radio = conf['radio']
        if conf['power']:
            power = conf['power']
            cmd = Template(SET_AP_RADIO_TX).substitute(dict(radio=radio, power=power))
            _do_excute_cmd(zdcli,cmd)
    
            
def _set_ap_radio_11n(zdcli,conf):   

    if conf['radio']:
        radio = conf['radio']
        if conf['n_mode']:
            n_mode = conf['n_mode']
            cmd = Template(SET_AP_RADIO_11N).substitute(dict(radio=radio, n_mode=n_mode))
            _do_excute_cmd(zdcli,cmd)


def _set_poe_port(zdcli,conf):
    if conf['poe_port']:
        cmd = SET_POE_PORT
        _do_excute_cmd(zdcli,cmd)
         

def _remove_poe_port(zdcli):
    cmd = REMOVE_POE_PORT
    _do_excute_cmd(zdcli,cmd)


def _set_ap_model(zdcli,conf):
    if conf['model']:
        cmd = Template(SET_AP_MODEL).substitute(dict(model = conf['model']))
        _do_excute_cmd(zdcli,cmd)
    
def _set_limited_zd_discovery(zdcli,conf):
    if conf['pri_zd_ip']:
        pri_zd_ip = conf['pri_zd_ip']
        if conf.has_key('sec_zd_ip'):
            sec_zd_ip = conf['sec_zd_ip']
        else:
            sec_zd_ip = ''
        
        cmd = Template(SET_LIMITED_ZD_DISCOVERY).substitute(dict(pri_zd_ip = pri_zd_ip,sec_zd_ip=sec_zd_ip))
        _do_excute_cmd(zdcli,cmd)
        
def _remove_limited_zd_discovery(zdcli):
    cmd = REMOVE_LIMITED_ZD_DISCOVERY
    _do_excute_cmd(zdcli,cmd)
        
def _set_led(zdcli,conf):
    if conf.has_key('led_conf'):
        led_conf = conf['led_conf']
        if led_conf['led']:
            cmd = Template(SET_LED).substitute(dict(led_model = conf['led_model']))
        
        else:
            cmd = Template(REMOVE_LED).substitute(dict(led_model = conf['led_model']))
        
        _do_excute_cmd(zdcli,cmd)


def _do_excute_cmd(zdcli,cmd):
    try:
        time.sleep(1)
        logging.info("CLI is: %s" %cmd)
        res = zdcli.do_cfg(cmd)        
        time.sleep(2)
        return res
    except Exception,ex:
        errmsg = ex.message
        raise Exception(errmsg)
 
def get_ap_policy(zdcli):
    cmd = ENTER_AP_POLICY        
    ap_policy_info = zdcli.do_cfg_show(cmd, print_out = True)
    data = {}
    if ap_policy_info:
        data = output.parse(ap_policy_info)
    return data