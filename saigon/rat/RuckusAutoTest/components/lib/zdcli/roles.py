'''
Created on 2011-3-15
@author: serena.tan@ruckuswireless.com
'''

import logging
from string import Template
from pprint import pformat

from RuckusAutoTest.components.lib.zdcli import get_wlan_info
from RuckusAutoTest.components.lib.zdcli import output_as_dict


CONFIG_ROLE_CMD_BLOCK = '''
role '$role_name'
'''
SET_ROLE_NAME = "name '$new_role_name'\n"
SET_ROLE_DESCRIPTION = "description '$description'\n"
SET_ROLE_GROUP_ATTRIBUTES = "group-attributes '$group_attr'\n"
SET_ROLE_WLAN_ALLOWED_ALL = "wlan-allowed all\n"
SET_ROLE_WLAN_ALLOWED_SPECIFY = "wlan-allowed specify-wlan\n"
SET_ROLE_SPECIFY_WLAN_ADD = "specify-wlan-access '$wlan_name'\n"
SET_ROLE_SPECIFY_WLAN_DELETE = "no specify-wlan-access '$wlan_name'\n"
SET_ROLE_GUEST_PASS_ENABLED = "guest-pass-generation\n"
SET_ROLE_GUEST_PASS_DISABLED = "no guest-pass-generation\n"
SET_ROLE_ADMIN_MODE = "admin '$zd_admin_mode'\n"
SET_ROLE_ADMIN_DISABLED = "no admin\n"
SET_ROLE_ENABLE_RBAC = 'access-ctrl\n'
SET_ROLE_DISABLE_RBAC = "no access-ctrl\n"
SET_ROLE_SPECIFY_OS_TYPE = 'os-type-allowed specify\n'
SET_ROLE_SPECIFY_OS_TYPE_ADD = 'specify-os-type-access "$os_type"\n'
SET_ROLE_ALL_OS_TYPE  = 'os-type-allowed all\n'
SET_ROLE_VLAN = 'vlan $vlan_number\n'
SET_ROLE_RATE = 'rate-limit uplink $rate_uplink downlink $rate_downlink\n'
SET_ROLE_RATE_DISABLE = 'no rate-limit\n'
SAVE_ROLE_CONFIG = "exit\n"

GET_ROLE_BY_NAME = "show role name '$role_name'"
GET_ALL_ROLES = "show role"

DELETE_ROLE = "no role '$role_name'"

ENTRY_NOT_FOUND_MSG = "The entry '$role_name' could not be found. Please check the spelling, and then try again."

ROLE_CFG_BASIC_KEY_LIST = ['role_name', 'description', 'groupt_attr', 'guest_pass_gen', 
                           'allow_all_wlans', 'specify_wlan_list', 'allow_zd_admin', 'zd_admin_mode',]


KEY_CONST = {'name':'Name',}

#--------------------------------------------------------------------------------------------------------------------------
#                                              PUBLIC METHODs   
    
def configure_single_role(zdcli, cfg):
    '''
    Input:
        cfg = {"role_name": "", 
               "new_role_name": "", 
               "allow_all_wlans": True/False,
               "specify_wlan_list": [], 
               "guest_pass_gen": True/False, 
               "description": "",
               "group_attr": "", 
               "allow_zd_admin": True/False,
               "zd_admin_mode": "super"/"operator"/"monitoring",
               "enable_rbac":True/False,
               "allow_all_os_type":True/False
               "specify_os_type":"Windows/Windows Mobile/Others/Android/BlackBerry/Apple iOS/Mac OS/Linux/VoIP/Gaming/Printers",
               "vlan_policy":10,
               "rate_limit_uplink":"0.10mbps",
               "rate_limit_downlink":"0.10mbps"
              }
    '''      
    conf = {"role_name": "", 
            "new_role_name": None, 
            "allow_all_wlans": None,
            "specify_wlan_list": None, 
            "guest_pass_gen": None, 
            "description": None,
            "group_attr": None, 
            "allow_zd_admin": None,
            "zd_admin_mode": None,
            "enable_rbac":False,
            "allow_all_os_type":None,
            "specify_os_type":[],
            "vlan_policy":None,
            "rate_limit_uplink":None,
            "rate_limit_downlink":None
          }
    conf.update(cfg)
    
    logging.info('Configure role in ZD CLI with cfg:\n%s' % pformat(cfg, 4, 120))
    value = _set_role(zdcli, conf)
    if not value:
        msg = 'Fail to configure role [%s] in ZD CLI' % conf['role_name']
        logging.info(msg)
        return (False, msg)
    
    #res, msg = _verify_role_cfg_in_cli(zdcli, conf)
    #if res:
    msg = 'Configure role [%s] in ZD CLI successfully' % conf['role_name']
    logging.info(msg)
    return (True, msg)
    
    #else:
        #logging.info(msg)
        #return (False, msg)
    

def delete_role_by_name(zdcli, role_name):
    """
    """
    _delete_role(zdcli, role_name)

def delete_all_roles(zdcli):
    roles = get_all_role_list(zdcli)
    for role in roles:
        role_name = role.get(KEY_CONST['name'])
        if role_name.strip() == 'Default':
            continue
        
        delete_role_by_name(zdcli, role_name)
    
    logging.info('Delete DONE')

def get_all_role_list(zdcli):
    cmd = Template(GET_ALL_ROLES).substitute(dict())
    data = zdcli.do_cfg(cmd, raw=True)
    data = data.get(GET_ALL_ROLES)[0]                
    data_dict = output_as_dict.parse(data)        
    info_dict = data_dict['Role']['ID']
    roles = info_dict.values()
    return roles

def get_role_info_by_name(zdcli, role_name):
    """
    Output:
        a dictionary of the role information:
            {'Name': '',
             'Allow All WLANs': 'Specify WLAN access'/'Allow access to all WLANs',
             ['Wlan': ['testing', 'testing1'],]
             'Guest Pass Generation': 'Allowed'/'Disallowed',
             'Description': '',
             'Group Attributes': '',
             'ZoneDirector Administration': 'Allowed'/'Disallowed',
             ['Allow ZoneDirector Administration': 'Super Admin'/'Operator Admin'/'Monitoring Admin',]
            }
        None: the wlan does not exist.
        raise exception
    """
    cmd = Template(GET_ROLE_BY_NAME).substitute(dict(role_name = role_name))
    no_entry_msg = Template(ENTRY_NOT_FOUND_MSG).substitute(dict(role_name = role_name))
    
    logging.info('Get information of role [%s] from ZD CLI by command [%s]' % (role_name, cmd))
    data = zdcli.do_show(cmd)
    if not data.startswith("Role:"):
        if no_entry_msg in data:
            logging.info('The role [%s] does not exist!' % role_name)
            return None
        
        else:
            raise Exception(data)
                        
    data_dict = output_as_dict.parse(data)
    info_dict = data_dict['Role']['ID']
    role_dict = info_dict.values()[0]
    logging.info('The information of role [%s] in ZD CLI is:\n%s' % (role_name, pformat(role_dict, 4, 120)))
    
    return role_dict
        

def verify_cli_admin_cfg_in_gui(cli_cfg_dict, gui_info_dict):
    '''
    Input:
    cli_cfg_dict = {"role_name": "", 
                    "new_role_name": "",     
                    "description": "",
                    "group_attr": "", 
                    "guest_pass_gen": True/False, 
                    "allow_all_wlans": True/False,
                    "specify_wlan_list": [], 
                    "allow_zd_admin": True/False,
                    "zd_admin_mode": "super"/"operator"/"monitoring",
                   }
    gui_info_dict = {"role_name": "", 
                     "description": "",
                     "group_attr": "", 
                     "guest_pass_gen": True/False, 
                     "allow_all_wlans": True/False,
                     "specify_wlan_list": [],    
                     "allow_zd_admin": True/False,
                     "zd_admin_mode": "super"/"operator"/"monitoring",    
                   }
    '''
    expect_info_dict = _define_expect_role_gui_info(cli_cfg_dict)
    logging.info("The expect information of role [%s] in ZD GUI is: %s" % (cli_cfg_dict['role_name'], pformat(expect_info_dict, 4, 120)))
        
    res, msg = _expect_is_in_dict(expect_info_dict, gui_info_dict)
    if res:
        msg = 'The role configuration of ZD CLI is showed correctly in ZD GUI!'
        logging.info(msg)
        return (True, msg)
    
    else:
        logging.info(msg)
        return (False, msg)


#--------------------------------------------------------------------------------------------------------------------------
#                                              UN-PUBLIC METHODs 
    
def _set_role(zdcli, cfg):
    all_wlan_list = []
    if cfg['specify_wlan_list'] != None:
        logging.info('Get all WLAN names from ZD CLI')
        all_wlan_list = get_wlan_info.get_all_wlan_name_list(zdcli)
        logging.info('All WLANs in ZD CLI are: %s' % all_wlan_list)
          
    cmd_block = _construct_configure_role_cmd_block(cfg, all_wlan_list)
    logging.info('Configure role with cmd_block:\n%s' % cmd_block)
    
    res = zdcli.do_cfg(cmd_block, raw = True)
    logging.info('cmd_block execution result:\n%s' % pformat(res, 4, 120))
    
    if "Your changes have been saved." not in res['exit'][0]:
        zdcli.back_to_priv_exec_mode(back_cmd = 'quit', print_out = True)
        return False
    
    return True


def _verify_role_cfg_in_cli(zdcli, cfg):
    new_role_name = cfg.pop('new_role_name')
    if new_role_name:
        cfg['role_name'] = new_role_name
        
    cli_info = get_role_info_by_name(zdcli, cfg['role_name'])
    expect_info = _define_expect_cli_info(cfg)
    logging.info("The expect information of role [%s] in ZD CLI is: %s" % (cfg['role_name'], pformat(expect_info, 4, 120)))
    
    return _expect_is_in_dict(expect_info, cli_info)


def _delete_role(zdcli, role_name):
    cmd_block = Template(DELETE_ROLE).substitute(dict(role_name = role_name))
    res = zdcli.do_cfg(cmd_block, raw = True)
    logging.info('cmd_block execution result:\n%s' % pformat(res, 4, 120))


def _construct_configure_role_cmd_block(cfg, all_wlan_list = []):  
    '''
    Input:
        a dict of the role configuration.
        cfg = {"role_name": "", 
               "new_role_name": "", 
               "allow_all_wlans": True/False,
               "specify_wlan_list": [], 
               "guest_pass_gen": True/False, 
               "description": "",
               "group_attr": "", 
               "allow_zd_admin": True/False,
               "zd_admin_mode": "super"/"operator"/"monitoring",
               "enable_rbac":True/False,
               "allow_all_os_type":True/False
               "specify_os_type":"Windows/Windows Mobile/Others/Android/BlackBerry/Apple iOS/Mac OS/Linux/VoIP/Gaming/Printers",
               "vlan_policy":10,
               "rate_limit_uplink":"0.10mbps",
               "rate_limit_downlink":"0.10mbps"
              }
        all_wlan_list: a list of all wlans in ZD.
    ''' 
    cmd_block = Template(CONFIG_ROLE_CMD_BLOCK).substitute(dict(role_name = cfg['role_name']))
    if cfg['new_role_name'] != None:
        cmd_block += Template(SET_ROLE_NAME).substitute(dict(new_role_name = cfg['new_role_name']))
     
    if cfg['allow_all_wlans'] == True:
        cmd_block += SET_ROLE_WLAN_ALLOWED_ALL
    
    elif cfg['allow_all_wlans'] == False:
        cmd_block += SET_ROLE_WLAN_ALLOWED_SPECIFY
    
    if cfg['specify_wlan_list'] != None:
        for no_wlan in all_wlan_list:
            cmd_block += Template(SET_ROLE_SPECIFY_WLAN_DELETE).substitute(dict(wlan_name = no_wlan))
        
        for add_wlan in cfg['specify_wlan_list']:
            cmd_block += Template(SET_ROLE_SPECIFY_WLAN_ADD).substitute(dict(wlan_name = add_wlan))
    
    if cfg['guest_pass_gen'] == True:
        cmd_block += SET_ROLE_GUEST_PASS_ENABLED
    
    elif cfg['guest_pass_gen'] == False:
        cmd_block += SET_ROLE_GUEST_PASS_DISABLED
    
    if cfg['description'] != None:
        cmd_block += Template(SET_ROLE_DESCRIPTION).substitute(dict(description = cfg['description']))
        
    if cfg['group_attr'] != None:
        cmd_block += Template(SET_ROLE_GROUP_ATTRIBUTES).substitute(dict(group_attr = cfg['group_attr']))
        
    if cfg['allow_zd_admin'] == True and cfg['zd_admin_mode']:
        cmd_block += Template(SET_ROLE_ADMIN_MODE).substitute(dict(zd_admin_mode = cfg['zd_admin_mode']))
    
    elif cfg['allow_zd_admin'] == False:
        cmd_block += SET_ROLE_ADMIN_DISABLED
        
    if cfg['enable_rbac'] == True:
        cmd_block += SET_ROLE_ENABLE_RBAC
        if cfg['specify_os_type']:
            cmd_block += SET_ROLE_SPECIFY_OS_TYPE
            for os_type in cfg['specify_os_type']:
                cmd_block += Template(SET_ROLE_SPECIFY_OS_TYPE_ADD).substitute(dict(os_type = os_type))
        
        if cfg['allow_all_os_type'] == True:
            cmd_block += SET_ROLE_ALL_OS_TYPE
       
        if cfg['vlan_policy'] != None:
            cmd_block += Template(SET_ROLE_VLAN).substitute(dict(vlan_number = cfg['vlan_policy']))
        
        if cfg['rate_limit_uplink'] != None and cfg['rate_limit_downlink'] != None:
            cmd_block += Template(SET_ROLE_RATE).substitute(dict(rate_uplink = cfg['rate_limit_uplink'],
                                                                 rate_downlink = cfg['rate_limit_downlink']))
        else:
            cmd_block += SET_ROLE_RATE_DISABLE
    else:
        cmd_block += SET_ROLE_DISABLE_RBAC
      
    cmd_block += SAVE_ROLE_CONFIG
    
    return cmd_block


def _define_expect_cli_info(cfg):
    '''
    Input:
    cfg = {"role_name": "", 
           "allow_all_wlans": True/False/None,
           "specify_wlan_list": [], 
           "guest_pass_gen": True/False/None, 
           "description": "",
           "group_attr": "", 
           "allow_zd_admin": True/False/None,
           "zd_admin_mode": "super"/"operator"/"monitoring",
          }
    Output:
    info = {'Name': '',
            'Allow All WLANs': {'Mode': 'Specify WLAN access'/'Allow access to all WLANs',
                                ['Wlan': ['testing', 'testing1'],]
                                }
            'Guest Pass Generation': 'Allowed'/'Disallowed',
            'Description': '',
            'Group Attributes': '',
            'ZoneDirector Administration': {'Status': 'Allowed'/'Disallowed',
                                            ['Allow ZoneDirector Administration': 'Super Admin'/'Operator Admin'/'Monitoring Admin',]
                                            }
            
           }
    '''       
    info = dict()
    if cfg['role_name']:
        info['Name'] = cfg['role_name']
    
    if cfg['description'] != None:
        info['Description'] = cfg['description']
    
    if cfg['group_attr'] != None:
        info['Group Attributes'] = cfg['group_attr']
    
    if cfg['guest_pass_gen'] == True:
        info['Guest Pass Generation'] = 'Allowed'
    
    elif cfg['guest_pass_gen'] == False:
        info['Guest Pass Generation'] = 'Disallowed'

    info['Allow All WLANs'] = {}
    if cfg['allow_all_wlans'] == True:
        info['Allow All WLANs']['Mode'] = 'Allow access to all WLANs'
    
    elif cfg['allow_all_wlans'] == False:
        info['Allow All WLANs']['Mode'] = 'Allow Specify WLAN access'
    
    if cfg['specify_wlan_list'] != None:
        if len(cfg['specify_wlan_list']) == 1:
            info['Allow All WLANs']['Wlan'] = cfg['specify_wlan_list'][0]
        
        elif len(cfg['specify_wlan_list']) > 1:
            info['Allow All WLANs']['Wlan'] = cfg['specify_wlan_list']

    info['ZoneDirector Administration'] = {}
    if cfg['allow_zd_admin'] == False:
        info['ZoneDirector Administration']['Status'] = 'Disallowed'
        
    elif cfg['allow_zd_admin'] == True:
        info['ZoneDirector Administration']['Status'] = 'Allowed'
        if cfg['zd_admin_mode'] == 'super':
            info['ZoneDirector Administration']['Allow ZoneDirector Administration'] = 'Super Admin'
        
        elif cfg['zd_admin_mode'] == 'operator':
            info['ZoneDirector Administration']['Allow ZoneDirector Administration'] = 'Operator Admin'
        
        elif cfg['zd_admin_mode'] == 'monitoring':
            info['ZoneDirector Administration']['Allow ZoneDirector Administration'] = 'Monitoring Admin'
        
        else:
            raise Exception('Unexpect zd admin mode [%s]' % cfg['zd_admin_mode'])
    
    return info


def _define_expect_role_gui_info(cli_cfg_dict):
    conf = {"role_name": None, 
            "new_role_name": None, 
            "allow_all_wlans": None,
            "specify_wlan_list": None, 
            "guest_pass_gen": None, 
            "description": None,
            "group_attr": None, 
            "allow_zd_admin": None,
            "zd_admin_mode": None,
          }
    conf.update(cli_cfg_dict)
    
    if conf['new_role_name']:
        conf['role_name'] = conf['new_role_name']
    
    expect_info = dict()
    for k in conf:
        if k in ROLE_CFG_BASIC_KEY_LIST and conf[k] != None:
            expect_info[k] = conf[k]
    
    return expect_info


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

