'''
How To:
    tea.py u.zdcli.config_ap_setting

Created on Feb 10, 2011
@author: cwang@ruckuswireless.com

'''
import logging
import random
from string import Template

from RuckusAutoTest.components import (create_zd_cli_by_ip_addr,clean_up_rat_env)

default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin', shell_key = '!v54! CKQpcGkLBgVbYHWieLU9Y24SPpAeirqV')
SETTING_COMMAND = '''ap $mac
devname $device_name
description $description
gps $x,$y       
'''

COMMAND_INSTANCE = Template(SETTING_COMMAND)

def do_config():
    return create_zd_cli_by_ip_addr(**default_cfg)

def do_test(zdcli):
    cfg = dict(description = _generate_string(64), 
               device_name = _generate_string(64),                         
               latitude = '37.38813989',
               longitude = '-122.02586330',)
    ap_list = [dict(mac='ac:67:06:33:28:90'),
               ]
    ap_cfg = dict()
    for ap in ap_list:
        ap_cfg['mac'] = ap['mac']                        
        ap_cfg['description'] = _generate_string(64)
        device_name = _generate_string(64)
        ap_cfg['device_name'] = device_name
        ap_cfg['x'] = cfg['latitude']
        ap_cfg['y'] = cfg['longitude']
        logging.info('configure ap %s as %s' % (ap_cfg['mac'], ap_cfg))        
#        logging.info(COMMAND_INSTANCE.substitute(ap_cfg))    
        zdcli.do_cfg(COMMAND_INSTANCE.substitute(ap_cfg))
    
    return ('PASS')        

def do_cleanup():
    clean_up_rat_env()


def main(**kwargs):
    do_test(do_config())
    do_cleanup()

def _generate_string(size):
    char_string = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    result = ''        
    random.seed()
    while size>0:
        lgt = len(char_string)
        index = random.randrange(0, lgt)
        result += char_string[index]
        size = size - 1
    return result    

if __name__ == '__main__':
    main()