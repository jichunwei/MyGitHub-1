'''
Created on 2011-1-18
@author: serena.tan@ruckuswireless.com

Description: This script is used to configure WLAN groups in ZD CLI.

Argument:
    zd_ip_addr: default value is '192.168.0.2'
    username:   default value is 'admin'
    password:   default value is 'admin'
    shell_key:  default value is '!v54!'
    wg_cfg_list: a list of the servers cfg

Examples: 
tea.py u.zdcli.configure_wlan_groups wg_cfg_list=[] shell_key='!v54! xxx' 
'''


from RuckusAutoTest.components import create_zd_cli_by_ip_addr
from RuckusAutoTest.components.lib.zdcli import configure_wlan_groups as cwg


wg_cfg_list = [{'wg_name': 'Default', 
                'wlan_member': {'ruckus_1': {},
                                'ruckus_2': {'vlan_override': 'none'},
                                'ruckus_3': {'vlan_override': 'untag'}, 
                                'ruckus_4': {'vlan_override': 'tag', 'tag_override': '302'}
                                }
                },
                {'wg_name': 'Wlan-Group-Testing',
                 'new_wg_name': 'New-Wlan-Group-Testing', 
                 'description': 'Wlan Group for Testing',
                 'wlan_member':{'ruckus_1': {},
                                'ruckus_2': {'vlan_override': 'none'},
                                'ruckus_3': {'vlan_override': 'untag'}, 
                                'ruckus_4': {'vlan_override': 'tag', 'tag_override': '302'}
                                }
                }
               ]


default_cfg = dict(zd_ip_addr = '192.168.0.2', 
                   username = 'admin', 
                   password = 'admin', 
                   shell_key = '!v54!',
                   wg_cfg_list = wg_cfg_list
                   )


def do_config(kwargs):
    cfg = default_cfg
    cfg.update(kwargs)
    
    cfg['zdcli'] = create_zd_cli_by_ip_addr(cfg['zd_ip_addr'], cfg['username'], cfg['password'], cfg['shell_key'])
    
    return cfg


def do_test(tcfg):
    res, msg = cwg.configure_wlan_groups(tcfg['zdcli'], tcfg['wg_cfg_list'])
    
    if res:
        return ("PASS", msg)
    
    else:
        return ("Fail", msg)

  
def do_clean_up(zdcli):
    del(zdcli)


def main(**kwargs):
    tcfg = do_config(kwargs)
    res = None  
    try:
        res = do_test(tcfg)
    finally:
        do_clean_up(tcfg)
    return res
