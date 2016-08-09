'''
Created on 2012-10-9
created by west.li
'''
import re
import copy
import logging
from string import Template
from pprint import pformat
from RuckusAutoTest.components.lib.zdcli import output_as_dict as output
#import copy
#import time
#import os
#
#from RuckusAutoTest.common import lib_Constant as const
#from RuckusAutoTest.components.lib.zdcli import ap_info_cli

CONFIG_AP_GRP_CMD_BLOCK = '''
ap-group '$grp_name'
'''

SET_MODEL_MAX_CLIENTS= "model $model max-clients $number\n"
SET_DISCRIPTION = "description $description\n"
SET_IPMODE = "ipmode $ipmode\n"
SET_RADIO_CHANNELIZATION='radio $radio channelization number $channelization\n'
SET_RADIO_CHANNELIZATION_AUTO='radio $radio channelization auto\n'
SET_RADIO_CHANNEL = 'radio $radio channel number $channel\n'
SET_RADIO_CHANNEL_AUTO = 'radio $radio channel auto\n'
SET_RADIO_TX_POWER = 'radio $radio tx-power Num $power\n'
SET_RADIO_TX_POWER_MIN = 'radio $radio tx-power Min\n'
SET_RADIO_11N_ONLY = 'radio $radio 11n-only $value\n'
SET_RADIO_WLAN_GRP = 'radio $radio wlan-group $wlan_grp\n'
SET_RADIO_ADM_CTL = 'radio $radio admission-control $limit\n'
ADD_AP_MEMBER = 'member add mac $ap_mac\n'
#@author: chen.tao since 2014-10, to enable lldp settings from zdcli
SET_LLDP_STATE_ENABLE = "lldp enable\n"
SET_LLDP_STATE_DISABLE = "lldp disable\n"
SET_LLDP_STATE_OTHER = "lldp %s\n"
SET_LLDP_INTERVAL = "lldp interval %s\n" #interval between 1 and 300, default is 30.
SET_LLDP_HOLDTIME = "lldp holdtime %s\n" #holdtime between 60 and 1200, default is 120.
SET_LLDP_PORT_ENABLE = "lldp ifname eth %s enable\n"
SET_LLDP_PORT_DISABLE = "lldp ifname eth %s disable\n"
SET_LLDP_MGMT_ENABLE = "lldp mgmt enable\n"
SET_LLDP_MGMT_DISABLE = "lldp mgmt disable\n"
SET_LLDP_MGMT_OTHER = "lldp mgmt %s\n"
SAVE_AP_GRP_CONFIG = "exit\n"

def new_ap_group(zdcli,conf):
    return _cfg_ap_grp(zdcli,conf)

def edit_ap_group(zdcli,conf):
    return _cfg_ap_grp(zdcli,conf)

def _cfg_ap_grp(zdcli,conf={}):
    '''
    input
    conf={  'name':'System Default',
            'description':'',
            'ip_mode':'',#ipv4, ipv6 or dual
            'radio2.4':{'channelization':'',
                       'channel':'',
                       'power':'',
                       '11n-only':'',#Auto,N-only
                       'wlan-grp':'',
                       'admission-ctl':'',
                       },
            'radio5.0':{'channelization':'',
                       'channel':'',
                       'power':'',
                       '11n-only':'',
                       'wlan-grp':'',
                       'admission-ctl':'',
                       },
            'model':{'zf2942':{'max-client':'',
                               'ext-antenna':{},
                               'port':{},
                               },
                     'zf7363':{'max-client':'',
                               'ext-antenna':{},
                                'port':{}
                               }   
                     }
            'add_members':[]
            }
    '''
    cmd_block = Template(CONFIG_AP_GRP_CMD_BLOCK).substitute(dict(grp_name = conf['name']))
    if 'description' in conf and conf['description']:
        cmd_block+=Template(SET_DISCRIPTION).substitute(dict(description = conf['description']))
    if 'ip_mode' in conf and conf['ip_mode']:
        cmd_block+=Template(SET_IPMODE).substitute(dict(ipmode = conf['ip_mode']))
    
    if 'radio2.4' in conf and conf['radio2.4']:
        radio='2.4'
        radio_conf=conf['radio2.4']
        if 'channelization' in radio_conf and radio_conf['channelization']:
            if radio_conf['channelization'].lower()!='auto':
                cmd_block+=Template(SET_RADIO_CHANNELIZATION).substitute({'radio':radio,'channelization':radio_conf['channelization']})
            else:
                cmd_block+=Template(SET_RADIO_CHANNELIZATION_AUTO).substitute({'radio':radio})
                
        if 'channel' in radio_conf and radio_conf['channel']:
            if radio_conf['channel'].lower()!='auto':
                cmd_block+=Template(SET_RADIO_CHANNEL).substitute({'radio':radio,'channel':radio_conf['channel']})
            else:
                cmd_block+=Template(SET_RADIO_CHANNEL_AUTO).substitute({'radio':radio})
        
        if 'power' in radio_conf and radio_conf['power']:
            if radio_conf['power'].lower()!='min':
                cmd_block+=Template(SET_RADIO_TX_POWER).substitute({'radio':radio,'power':radio_conf['power']})
            else:
                cmd_block+=Template(SET_RADIO_TX_POWER_MIN).substitute({'radio':radio})
        
        if '11n-only' in radio_conf and radio_conf['11n-only']:
            cmd_block+=Template(SET_RADIO_11N_ONLY).substitute({'radio':radio,'value':radio_conf['11n-only']})
            
        if 'wlan-grp' in radio_conf and radio_conf['wlan-grp']:
            cmd_block+=Template(SET_RADIO_WLAN_GRP).substitute({'radio':radio,'wlan_grp':radio_conf['wlan-grp']})
            
        if 'admission-ctl' in radio_conf and radio_conf['admission-ctl']:
            cmd_block+=Template(SET_RADIO_ADM_CTL).substitute({'radio':radio,'limit':radio_conf['admission-ctl']})
            
    if 'radio5.0' in conf and conf['radio5.0']:
        radio='5'
        radio_conf=conf['radio5.0']
        #5.0 channel and channelization not support now bug zf-1004
#        if 'channelization' in radio_conf and radio_conf['channelization']:
#            if radio_conf['channelization'].lower()!='auto':
#                cmd_block+=Template(SET_RADIO_CHANNELIZATION).substitute({'radio':radio,'channelization':radio_conf['channelization']})
#            else:
#                cmd_block+=Template(SET_RADIO_CHANNELIZATION_AUTO).substitute({'radio':radio})
#                
#        if 'channel' in radio_conf and radio_conf['channel']:
#            if radio_conf['channel'].lower()!='auto':
#                cmd_block+=Template(SET_RADIO_CHANNEL).substitute({'radio':radio,'channel':radio_conf['channel']})
#            else:
#                cmd_block+=Template(SET_RADIO_CHANNEL_AUTO).substitute({'radio':radio})
#        
        if 'power' in radio_conf and radio_conf['power']:
            if radio_conf['power'].lower()!='min':
                cmd_block+=Template(SET_RADIO_TX_POWER).substitute({'radio':radio,'power':radio_conf['power']})
            else:
                cmd_block+=Template(SET_RADIO_TX_POWER_MIN).substitute({'radio':radio})
        
        if '11n-only' in radio_conf and radio_conf['11n-only']:
            cmd_block+=Template(SET_RADIO_11N_ONLY).substitute({'radio':radio,'value':radio_conf['11n-only']})
            
        if 'wlan-grp' in radio_conf and radio_conf['wlan-grp']:
            cmd_block+=Template(SET_RADIO_WLAN_GRP).substitute({'radio':radio,'wlan_grp':radio_conf['wlan-grp']})
            
        if 'admission-ctl' in radio_conf and radio_conf['admission-ctl']:
            cmd_block+=Template(SET_RADIO_ADM_CTL).substitute({'radio':radio,'limit':radio_conf['admission-ctl']})
            
    
    if 'model' in conf and conf['model']:
        for model in conf['model']:
            model_conf=conf['model'][model]
            if 'max-client' in model_conf and model_conf['max-client']:
                cmd_block += Template(SET_MODEL_MAX_CLIENTS).substitute({'model':model,'number':model_conf['max-client']})
            if 'ext-antenna' in model_conf and model_conf['ext-antenna']:
                pass
            if 'port' in model_conf and model_conf['port']:
                pass
    if 'add_members' in conf and conf['add_members']:
        for member in conf['add_members']:
            cmd_block += Template(ADD_AP_MEMBER).substitute({'ap_mac':member})

#@author: chen.tao since 2014-10, to enable lldp settings from zdcli
    if conf.get('lldp'):
        if conf['lldp'].get('state') == 'enable':
            cmd_block += SET_LLDP_STATE_ENABLE
        elif conf['lldp'].get('state') == 'disable':
            cmd_block += SET_LLDP_STATE_DISABLE
        elif conf['lldp'].get('state'):
            cmd_block += SET_LLDP_STATE_OTHER%conf['lldp']['state']
        if conf['lldp'].get('interval'):
            cmd_block += SET_LLDP_INTERVAL%conf['lldp']['interval']
        if conf['lldp'].get('holdtime'):
            cmd_block += SET_LLDP_HOLDTIME%conf['lldp']['holdtime']
        if conf['lldp'].get('mgmt') == 'enable':
            cmd_block += SET_LLDP_MGMT_ENABLE
        elif conf['lldp'].get('mgmt') == 'disable':
            cmd_block += SET_LLDP_MGMT_DISABLE
        elif conf['lldp'].get('mgmt'):
            cmd_block += SET_LLDP_MGMT_OTHER%conf['lldp']['mgmt']
        if conf['lldp'].get('enable_ports'):
            for port in conf['lldp']['enable_ports']:
                cmd_block += SET_LLDP_PORT_ENABLE%port
        if conf['lldp'].get('disable_ports'):
            for port in conf['lldp']['disable_ports']:
                cmd_block += SET_LLDP_PORT_DISABLE%port
    cmd_block += SAVE_AP_GRP_CONFIG
    res = zdcli.do_cfg(cmd_block, timeout=180, raw = True)
    logging.info('cmd_block execution result:\n%s' % pformat(res, 4, 120))
    
    if "Your changes have been saved." not in res['exit'][0]:
        zdcli.back_to_priv_exec_mode(back_cmd = 'quit', print_out = True)
        return (False, res)
#@author: chen.tao since 2014-10, to enable lldp settings from zdcli
    if conf.has_key('lldp'):
        res, msg = _verify_apgrp_lldp_cfg_in_cli(zdcli, conf)
        if not res:
            err_msg = 'Fail to configure AP group lldp config in ZD CLI [%s]' % (msg)
            logging.info(err_msg)
            return (False, err_msg)
    return (True, "")

#@author: chen.tao since 2014-10, to enable lldp settings from zdcli
def _verify_apgrp_lldp_cfg_in_cli(zdcli,cfg):
    conf = copy.deepcopy(cfg)
    grp_name = conf.pop('name')
    ap_grp_info = _get_ap_grp_lldp_cfg_raw_dict(zdcli, grp_name)
    if ap_grp_info == None:
        return (False, 'AP group [%s] does not exist.' % grp_name)
    
    expect_info = _define_expect_ap_group_info_in_cli(conf)
    logging.info("The expect ap group info in ZD CLI is: %s" % pformat(expect_info, 4, 120))
    
    return _expect_is_in_dict(expect_info, ap_grp_info)

#@author: chen.tao since 2014-10, to enable lldp settings from zdcli
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

#@author: chen.tao since 2014-10, to enable lldp settings from zdcli
def _define_expect_ap_group_info_in_cli(conf):
    expect_info = {}
    if conf.has_key('lldp'):
        expect_info['LLDP'] = {}
        if conf['lldp'].get('state') == 'enable':
            expect_info['LLDP']['Status'] = 'Enabled'
        elif conf['lldp'].get('state') == 'disable':
            expect_info['LLDP']['Status'] = 'Disabled'
        elif conf['lldp'].get('state'):
            expect_info['LLDP']['Status'] = conf['lldp']['state']
        if conf['lldp'].get('interval'):
            expect_info['LLDP']['Interval'] = conf['lldp']['interval']
        if conf['lldp'].get('holdtime'):
            expect_info['LLDP']['HoldTime'] = conf['lldp']['holdtime']
        if conf['lldp'].get('mgmt') == 'enable':
            expect_info['LLDP']['Mgmt'] = 'Enabled'
        elif conf['lldp'].get('mgmt') == 'disable':
            expect_info['LLDP']['Mgmt'] = 'Disabled'
        elif conf['lldp'].get('mgmt'):
            expect_info['LLDP']['Mgmt'] = conf['lldp']['mgmt']
        if conf['lldp'].get('enable_ports') or conf['lldp'].get('disable_ports'):
            expect_info['LLDP']['Ports'] ={}
            if conf['lldp'].get('enable_ports'):
                for port in conf['lldp']['enable_ports']:
                    expect_info['LLDP']['Ports']['Send out LLDP packet on eth%s'%str(port)] = 'Enabled'
            if conf['lldp'].get('disable_ports'):
                for port in conf['lldp']['disable_ports']:
                    expect_info['LLDP']['Ports']['Send out LLDP packet on eth%s'%str(port)] = 'Disabled'

    return expect_info   

def set_model_max_clients_number(
        zdcli, ap_grp,model,number
    ):    
    number=str(number)
    cmd_block = Template(CONFIG_AP_GRP_CMD_BLOCK).substitute(dict(grp_name = ap_grp))
    cmd_block += Template(SET_MODEL_MAX_CLIENTS).substitute({'model':model,'number':number})
    cmd_block += SAVE_AP_GRP_CONFIG
    res = zdcli.do_cfg(cmd_block, raw = True)
    logging.info('cmd_block execution result:\n%s' % pformat(res, 4, 120))
    
    if "Your changes have been saved." not in res['exit'][0]:
        zdcli.back_to_priv_exec_mode(back_cmd = 'quit', print_out = True)
        return (False, res)
    
    return (True, "")


def set_multi_model_max_clients_number(
        zdcli, ap_grp,max_dict
    ):    
    '''
    max_dict={'zf7372':'20',
         'zf7363':'100',
         'zf2942':'50',
        }
    '''
    cmd_block = Template(CONFIG_AP_GRP_CMD_BLOCK).substitute(dict(grp_name = ap_grp))
    for model in max_dict:
        number=str(max_dict[model])
        cmd_block += Template(SET_MODEL_MAX_CLIENTS).substitute({'model':model,'number':number})
    cmd_block += SAVE_AP_GRP_CONFIG
    res = zdcli.do_cfg(cmd_block, raw = True)
    logging.info('cmd_block execution result:\n%s' % pformat(res, 4, 120))
    
    if "Your changes have been saved." not in res['exit'][0]:
        zdcli.back_to_priv_exec_mode(back_cmd = 'quit', print_out = True)
        return (False, res)
    
    return (True, "")

def get_all_model_max_client_number(zdcli,ap_grp):
    '''
    return
    {'zf7372':'20',
     'zf7363':'100',
     'zf2942':'50',
    }
    '''
    result={}
    ap_grp_info=_get_ap_grp_info(zdcli,ap_grp)
    for id in ap_grp_info['ID']:#only one id in the dict ap_grp_info['ID']
        info=ap_grp_info['ID'][id]
        if 'Model' in info:
            model_list=info['Model']
            if type(model_list) == dict:
                model_list = [model_list]
        else:
            logging.info('no model has been modified')
            return result
    for model in model_list:
        result[model['Name']]=model['Max. clients']
    return result
	
#@author: chen.tao since 2014-10, to enable lldp settings from zdcli
def _get_ap_grp_lldp_cfg_raw_dict(zdcli,ap_grp):

    ap_grp_info = _get_ap_grp_info(zdcli,ap_grp)
    ap_grp_info = ap_grp_info['ID'].values()[0]
   
    return ap_grp_info

#@author: chen.tao since 2014-10, to enable lldp settings from zdcli
def get_ap_grp_lldp_cfg_dict(zdcli,ap_grp):

    ap_grp_info = _get_ap_grp_info(zdcli,ap_grp)
    ap_grp_info = ap_grp_info['ID'].values()[0]
    lldp_info = ap_grp_info['LLDP']
    lldp_info_dict = {'state':'',
                      'interval': '',
                      'holdtime': '',
                      'mgmt': ''
                          }
    lldp_info_dict['state'] = lldp_info['Status']
    lldp_info_dict['interval'] = lldp_info['Interval']
    lldp_info_dict['holdtime'] = lldp_info['HoldTime']
    lldp_info_dict['mgmt'] = lldp_info['Mgmt']
    pattern_lldp_eth = '(eth\d+)'
    lldp_info_dict['enable_ports']=[]
    lldp_info_dict['disable_ports']=[]
    for port,status in lldp_info['Ports'].iteritems(): 
        port_name = re.search(pattern_lldp_eth,port).group(1)
        #lldp_info_dict[interface_name] = status
        if status == 'Enabled':
            lldp_info_dict['enable_ports'].append(port_name)
        if status == 'Disabled':
            lldp_info_dict['disable_ports'].append(port_name)   
    return lldp_info_dict

def _get_ap_grp_info(zdcli,ap_grp):
    '''
    return
    {'ID': {'3': {'Radio 11bgn': {'Call Admission Control': '20% airtime usage limit', 
                                  'Channelization': '40', 
                                  'Tx. Power': '-5dB', 
                                  '11N only Mode': 'N-only', 
                                  'WLAN Group': 'Default', 
                                  'Channel': '1'}, 
                  'Name': 'new1', 
                  'Description': 'new1_1', 
                  'Radio 11an': {'Call Admission Control': '10% airtime usage limit', 
                                 'Channelization': 'Auto', 
                                 'Tx. Power': '-5dB', 
                                 '11N only Mode': 'Auto', 
                                 'WLAN Group': 'new_test', 
                                 'Channel': 'Auto'}, 
                  'Model': [{'Max. clients': '20', 
                            'Override System Default AP Group Port Setting': 'No', 
                            'Name': 'zf2942'}, 
                            {'Max. clients': '50', 
                             'Override System Default AP Group Port Setting': 'No', 
                             'Name': 'zf7363', 
                             'Disable Status-LEDs': 'No'}, 
                            {'Max. clients': '20', 
                             'Override System Default AP Group Port Setting': 'No', 
                             'Name': 'zf7372'}], 
                 'Network Setting': {'Protocol mode': 'IPv4 and IPv6'}
                 }
             }
     }
     
    '''
    cmd = Template(CONFIG_AP_GRP_CMD_BLOCK).substitute(dict(grp_name = ap_grp))
    res = zdcli.do_cfg_show(cmd) 
    rr = output.parse(res,break_if_error=False)  
    return rr['APGROUP']

      
if __name__ == '__main__':
    from ratenv import *
    from RuckusAutoTest.components import create_zd_cli_by_ip_addr
    zdcli=create_zd_cli_by_ip_addr()
    new1_max=get_model_max_client_number(zdcli,'new1')
    new_max=get_model_max_client_number(zdcli,'new')
    
    print('new1 client%s'%new1_max)
    print('new client%s'%new_max)
#    conf={'name':'new2',
#        'description':'new2',
#        'ip_mode':'ipv4',#ipv4, ipv6 or dual
#        'radio2.4':{'channelization':'auto',
#                   'channel':'auto',
#                   'power':'min',
#                   '11n-only':'auto',#Auto,N-only
#                   'wlan-grp':'new_test',
#                   'admission-ctl':'10',
#                   },
#        'radio5.0':{'channelization':'',
#                   'channel':'',
#                   'power':'6',
#                   '11n-only':'N-only',
#                   'wlan-grp':'Default',
#                   'admission-ctl':'20',
#                   },
#        'model':{'zf2942':{'max-client':'10',
#                           'ext-antenna':{},
#                           'port':{},
#                           },
#                 'zf7363':{'max-client':'100',
#                           'ext-antenna':{},
#                            'port':{}
#                           }   
#                 }
#        }
#    new_ap_group(zdcli,conf)
#    import pdb
#    pdb.set_trace()
#    conf={'name':'new2',
#        'description':'new2_1',
#        'ip_mode':'dual',#ipv4, ipv6 or dual
#        'radio2.4':{'channelization':'40',
#                   'channel':'1',
#                   'power':'5',
#                   '11n-only':'N-only',#Auto,N-only
#                   'wlan-grp':'Default',
#                   'admission-ctl':'20',
#                   },
#        'radio5.0':{'channelization':'',
#                   'channel':'',
#                   'power':'5',
#                   '11n-only':'auto',
#                   'wlan-grp':'new_test',
#                   'admission-ctl':'10',
#                   },
#        'model':{'zf2942':{'max-client':'20',
#                           'ext-antenna':{},
#                           'port':{},
#                           },
#                 'zf7363':{'max-client':'50',
#                           'ext-antenna':{},
#                            'port':{}
#                           }   
#                 }
#        }
#    edit_ap_group(zdcli,conf)
                
        
        
            
        
