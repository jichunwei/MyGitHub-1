'''
Created on 2011-2-15
@author: serena.tan@ruckuswireless.com

Description: This script is used to configure APs in ZD CLI.

Argument:
    zd_ip_addr: default value is '192.168.0.2'
    username:   default value is 'admin'
    password:   default value is 'admin'
    shell_key:  default value is '!v54!'
    ap_cfg_list: a list of the servers cfg

Examples: 
tea.py u.zdcli.config_ap ap_cfg_list=[] shell_key='!v54! xxx' 
'''


from RuckusAutoTest.components import create_zd_cli_by_ip_addr
from RuckusAutoTest.components.lib.zdcli import configure_ap


ap_cfg_list =[{'mac_addr': 'ac:67:06:33:76:b0', 'device_name': 'RuckusAP', 'description': 'Testing', 
               'location': '', 'mesh_mode': 'auto', 'mesh_uplink_mode': '', 
               'mesh_uplink_aps': [],
               'gps_coordinates': {'latitude': '37.3881398',
                                    'longitude': '-122.0258633',
                                },
               'network_setting': {'ip_mode': 'static',
                                   'ip_addr': '192.168.0.20',
                                   'net_mask': '255.255.255.0',
                                   'gateway': '192.168.0.2',
                                   'pri_dns': '192.168.0.252',
                                   'sec_dns': '192.168.0.253',
                                },
               'radio_bg': {'channel': '5',
                            'channelization': 'Auto',
                            'power': 'Auto',
                            'wlangroup': '',
                            },
               'radio_na': {'channel': '48',
                            'channelization': '20',
                            'power': 'Full',
                            'wlangroup': '',
                            },
        },]

default_cfg = dict(zd_ip_addr = '192.168.0.2', 
                   username = 'admin', 
                   password = 'admin', 
                   shell_key = '!v54! zqrODRKoyUMq1KNjADvhGeU7tgjt56ap',
                   ap_cfg_list = ap_cfg_list
                   )


def do_config(kwargs):
    cfg = default_cfg
    cfg.update(kwargs)
    
    cfg['zdcli'] = create_zd_cli_by_ip_addr(cfg['zd_ip_addr'], cfg['username'], cfg['password'], cfg['shell_key'])
    
    return cfg


def do_test(tcfg):
    res, msg = configure_ap.configure_aps(tcfg['zdcli'], tcfg['ap_cfg_list'])
    
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
