'''
Created on Jan 19, 2011
@author: cwang@ruckuswireless.com

Reboot all of APs and make sure ZD doesn't crash.

'''
import time
import logging
from RuckusAutoTest.components import create_zd_cli_by_ip_addr
from RuckusAutoTest.components import clean_up_rat_env

default_cfg = dict(ip_addr = '192.168.0.2', 
                   username = 'admin', 
                   password = 'admin', 
                   shell_key = '!v54! LWRLz@tZAOFoz.gnqM9LZyflW@hR1DBB',
                   )
ap_list =  [u'00:13:24:01:03:90',
               u'00:13:26:01:03:90',
               u'00:13:20:01:03:90',
               u'00:13:28:01:03:90',
               u'00:13:21:01:03:90',
               u'00:13:25:01:03:90',
               u'00:13:29:01:03:90',
               u'00:13:22:01:03:90',
               u'00:13:27:01:03:90',
               u'00:13:29:01:04:90',
               u'00:13:28:01:03:c0',
               u'00:13:26:01:03:c0',
               u'00:13:21:01:02:10',
               u'00:13:24:01:02:e0',
               u'00:13:20:01:02:90',
               u'00:13:29:01:02:90',
               u'00:13:24:01:03:d0',
               u'00:13:28:01:04:30',
               u'00:13:20:01:02:60',
               u'00:13:26:01:04:30',
               u'00:13:28:01:03:10',
               u'00:13:27:01:03:10',
               u'00:13:20:01:03:10',
               u'00:13:29:01:03:10',
               u'00:13:22:01:03:d0',
               u'00:13:21:01:04:c0',
               u'00:13:26:01:03:d0',
               u'00:13:27:01:03:d0',
               u'00:13:28:01:03:d0',
               u'00:13:25:01:03:d0',
               u'00:13:20:01:03:d0',
               u'00:13:21:01:03:d0',
               u'00:13:20:01:02:30',
               u'00:13:22:01:02:30',
               u'00:13:24:01:02:30',
               u'00:13:26:01:03:20',
               u'00:13:29:01:03:20',
               u'00:13:29:01:02:30',
               u'00:13:28:01:03:20',
               u'00:13:22:01:03:20',
               u'00:13:20:01:03:20',
               u'00:13:25:01:02:30',
               u'00:13:29:01:04:e0',
               u'00:13:27:01:04:d0',
               u'00:13:25:01:04:d0',
               u'00:13:20:01:04:d0',
               u'00:13:22:01:04:d0',
               u'00:13:21:01:04:20',
               u'00:13:28:01:02:40',
               u'00:13:28:01:04:d0',
               u'00:13:21:01:04:d0',
               u'00:13:29:01:04:d0',
               u'00:13:26:01:04:d0',
               u'04:4f:aa:02:72:30',
               u'00:13:29:01:02:10',
               u'00:13:26:01:02:10',
               u'00:13:20:01:02:10',
               u'00:13:22:01:02:10',
               u'00:13:25:01:04:30',
               u'00:13:26:01:02:60',
               u'00:13:25:01:02:10',
               u'00:13:24:01:02:10',
               u'00:13:29:01:02:60',
               u'00:13:29:01:03:40',
               u'00:13:24:01:04:30',
               u'00:13:29:01:04:30',
               u'00:13:22:01:02:60',
               u'00:13:27:01:04:30',
               u'00:13:25:01:02:60',
               u'00:13:20:01:03:40',
               u'00:13:27:01:02:70',
               u'00:13:22:01:02:70',
               u'00:13:29:01:02:70',
               u'00:13:26:01:02:70',
               u'00:13:21:01:02:70',
               u'00:13:24:01:02:70',
               u'00:13:28:01:02:70',
               u'00:13:20:01:02:70',
               u'00:13:25:01:05:10',
               u'00:13:29:01:05:10',
               u'00:13:22:01:02:b0',
               u'00:13:26:01:02:b0',
               u'00:13:28:01:02:b0',
               u'00:13:25:01:02:b0',
               u'00:13:25:01:04:10',
               u'00:13:21:01:04:10',
               u'00:13:26:01:04:10',
               u'00:13:29:01:04:10',
               u'00:13:28:01:02:20',
               u'00:13:22:01:02:20',
               u'00:13:24:01:02:c0',
               u'00:13:24:01:04:60',
               u'00:13:22:01:03:b0',
               u'00:13:25:01:03:b0',
               u'00:13:20:01:03:b0',
               u'00:13:29:01:03:b0',
               u'00:13:26:01:03:b0',
               u'00:13:28:01:03:b0',
               u'00:13:21:01:04:60',
               u'00:13:26:01:04:60',
               u'00:13:25:01:02:00',
               u'00:13:20:01:04:00',
               u'00:13:21:01:02:00',
               u'00:13:20:01:05:00',
               u'00:13:24:01:05:00',
               u'00:13:28:01:03:00',
               u'00:13:22:01:03:00',
               u'00:13:27:01:03:00',
               u'00:13:29:01:05:00',
               u'00:13:25:01:03:40',
               u'00:13:29:01:03:d0',
               u'00:13:26:01:04:90',
               u'00:13:24:01:04:90',
               u'00:13:25:01:03:f0',
               u'00:13:20:01:03:f0',
               u'00:13:22:01:03:f0',
               u'00:13:26:01:03:f0',
               u'00:13:27:01:03:f0',
               u'00:13:29:01:03:c0',
               u'00:13:20:01:04:90',
               u'00:13:27:01:03:c0',
               u'00:13:21:01:03:10',
               u'00:13:25:01:03:10',
               u'00:13:20:01:03:a0',
               u'00:13:29:01:03:a0',
               u'00:13:29:01:02:f0',
               u'00:13:27:01:03:a0',
               u'00:13:22:01:02:f0',
               u'00:13:22:01:03:a0',
               u'00:13:25:01:03:a0',
               u'00:13:27:01:02:f0',
               u'00:13:26:01:03:a0',
               u'00:13:28:01:02:f0',
               u'00:13:27:01:02:60',
               u'00:13:27:01:03:40',
               u'00:13:21:01:03:40',
               u'00:13:22:01:04:30',
               u'00:13:24:01:02:60',
               u'00:13:21:01:02:60',
               u'00:13:20:01:04:30',
               u'00:13:28:01:03:40',
               u'00:13:22:01:03:40',
               u'00:13:26:01:03:40',
               u'00:13:27:01:03:20',
               u'00:13:21:01:02:30',
               u'00:13:27:01:02:10',
               u'00:13:26:01:02:30',
               u'00:13:28:01:02:30',
               u'00:13:28:01:03:50',
               u'00:13:22:01:03:50',
               u'00:13:21:01:03:20',
               u'00:13:27:01:02:30',
               u'00:13:24:01:03:20',
               u'00:13:25:01:03:20',
               u'00:13:22:01:04:10',
               u'00:13:27:01:02:d0',
               u'00:13:25:01:02:d0',
               u'00:13:28:01:02:d0',
               u'00:13:24:01:04:b0',
               u'00:13:28:01:04:b0',
               u'00:13:22:01:04:b0',
               u'00:13:27:01:04:b0',
               u'00:13:26:01:04:b0',
               u'00:13:22:01:02:d0',
               u'00:13:29:01:02:d0',
               u'00:13:27:01:03:b0',
               u'00:13:21:01:03:b0',
               u'00:13:26:01:03:e0',
               u'00:13:24:01:03:b0',
               u'00:13:25:01:03:e0',
               u'00:13:24:01:03:e0',
               u'00:13:21:01:03:e0',
               u'00:13:27:01:03:e0',
               u'00:13:28:01:03:e0',
               u'00:13:29:01:03:e0',
               u'00:13:20:01:04:50',
               u'00:13:21:01:04:50',
               u'00:13:27:01:02:a0',
               u'00:13:22:01:02:a0',
               u'00:13:25:01:04:50',
               u'00:13:24:01:02:a0',
               u'00:13:28:01:04:50',
               u'00:13:20:01:02:a0',
               u'00:13:27:01:04:50',
               u'00:13:25:01:02:a0',
               u'00:13:21:01:02:90',
               u'00:13:26:01:02:90',
               u'00:13:29:01:04:80',
               u'00:13:22:01:04:80',
               u'00:13:20:01:04:80',
               u'00:13:24:01:04:80',
               u'00:13:25:01:04:80',
               u'00:13:27:01:04:80',
               u'00:13:21:01:04:80',
               u'00:13:26:01:04:80',
               u'00:13:25:01:02:70',
               u'00:13:28:01:04:80',
               u'00:13:28:01:02:a0',
               u'00:13:22:01:04:50',
               u'00:13:29:01:02:a0',
               u'00:13:29:01:04:50',
               u'00:13:26:01:04:50',
               u'00:13:21:01:02:a0',
               u'00:13:20:01:04:e0',
               u'00:13:22:01:04:e0',
               u'00:13:27:01:02:20',
               u'00:13:27:01:04:10',
               u'00:13:26:01:02:20',
               u'00:13:29:01:02:20',
               u'00:13:21:01:02:20',
               u'00:13:25:01:02:20',
               u'00:13:20:01:02:20',
               u'00:13:24:01:04:50',
               u'00:13:29:01:03:60',
               u'00:13:20:01:03:60',
               u'00:13:24:01:02:80',
               u'00:13:22:01:04:40',
               u'00:13:28:01:02:80',
               u'00:13:26:01:02:80',
               u'00:13:25:01:02:80',
               u'00:13:24:01:04:d0',
               u'00:13:21:01:02:80',
               u'00:13:25:01:04:40',
               u'00:13:29:01:04:40',
               u'00:13:20:01:04:40',
               u'00:13:28:01:03:80',
               u'00:13:27:01:03:50',
               u'00:13:20:01:04:60',
               u'00:13:26:01:02:c0',
               u'00:13:20:01:03:50',
               u'00:13:24:01:03:50',
               u'00:13:25:01:03:50',
               u'00:13:21:01:03:50',
               u'00:13:29:01:03:50',
               u'00:13:26:01:03:50',
               u'00:13:25:01:04:00',
               u'00:13:24:01:02:00',
               u'00:13:26:01:04:00',
               u'00:13:24:01:03:00',
               u'00:13:24:01:04:00',
               u'00:13:27:01:05:00',
               u'00:13:27:01:04:00',
               u'00:13:22:01:05:00',
               u'00:13:26:01:05:00',
               u'00:13:26:01:03:00',
               u'00:13:28:01:03:f0',
               u'00:13:21:01:03:f0',
               u'00:13:22:01:02:50',
               u'00:13:29:01:02:50',
               u'00:13:26:01:02:50',
               u'00:13:24:01:02:50',
               u'00:13:21:01:02:50',
               u'00:13:27:01:02:50',
               u'00:13:24:01:03:f0',
               u'00:13:29:01:03:f0',
               u'00:13:27:01:04:e0',
               u'00:13:24:01:02:f0',
               u'00:13:21:01:02:f0',
               u'00:13:25:01:02:f0',
               u'00:13:26:01:02:f0',
               u'00:13:21:01:03:a0',
               u'00:13:24:01:03:a0',
               u'00:13:28:01:03:a0',
               u'00:13:20:01:02:f0',
               u'00:13:25:01:03:70',
               u'00:13:20:01:03:70',
               u'00:13:25:01:02:50',
               u'00:13:28:01:02:50',
               u'00:13:25:01:04:70',
               u'00:13:26:01:02:e0',
               u'00:13:27:01:02:e0',
               u'00:13:28:01:04:70',
               u'00:13:29:01:02:e0',
               u'00:13:20:01:02:50',
               u'00:13:21:01:02:e0',
               u'00:13:20:01:02:e0',
               u'00:13:26:01:04:e0',
               u'00:13:21:01:04:e0',
               u'00:13:20:01:04:a0',
               u'00:13:24:01:04:a0',
               u'00:13:24:01:05:10',
               u'00:13:27:01:05:10',
               u'00:13:26:01:05:10',
               u'00:13:22:01:05:10',
               u'00:13:28:01:05:10',
               u'00:13:20:01:05:10',
               u'00:13:28:01:04:a0',
               u'00:13:29:01:04:a0',
               u'00:13:26:01:02:d0',
               u'00:13:21:01:02:d0',
               u'00:13:24:01:02:d0',
               u'00:13:20:01:02:d0',
               u'00:13:28:01:04:20',
               u'00:13:29:01:04:20',
               u'00:13:27:01:04:20',
               u'00:13:26:01:04:20',
               u'00:13:21:01:02:40',
               u'00:13:20:01:02:40',
               u'00:13:24:01:03:60',
               u'00:13:22:01:03:60',
               u'00:13:28:01:02:90',
               u'00:13:26:01:03:60',
               u'00:13:27:01:03:60',
               u'00:13:27:01:02:90',
               u'00:13:22:01:03:e0',
               u'00:13:20:01:03:e0',
               u'00:13:25:01:04:f0',
               u'00:13:27:01:04:f0',
               u'00:13:24:01:04:f0',
               u'00:13:21:01:04:f0',
               u'00:13:29:01:04:f0',
               u'00:13:22:01:04:f0',
               u'00:13:20:01:04:f0',
               u'00:13:28:01:04:f0',
               u'00:13:26:01:02:00',
               u'00:13:29:01:02:00',
               u'00:13:29:01:04:00',
               u'00:13:22:01:02:00',
               u'00:13:28:01:04:00',
               u'00:13:21:01:03:00',
               u'00:13:20:01:02:00',
               u'00:13:27:01:02:00',
               u'00:13:21:01:04:00',
               u'00:13:25:01:05:00',
               u'00:13:25:01:03:c0',
               u'00:13:27:01:04:90',
               u'00:13:25:01:04:90',
               u'00:13:20:01:03:c0',
               u'00:13:28:01:04:90',
               u'00:13:24:01:03:c0',
               u'00:13:22:01:04:90',
               u'00:13:21:01:03:c0',
               u'00:13:22:01:03:c0',
               u'00:13:21:01:04:90',
               u'00:13:25:01:04:e0',
               u'00:13:28:01:04:e0',
               u'00:13:24:01:04:c0',
               u'00:13:25:01:04:c0',
               u'00:13:24:01:03:10',
               u'00:13:26:01:03:10',
               u'00:13:24:01:04:e0',
               u'00:13:22:01:03:10',
               u'00:13:26:01:04:c0',
               u'00:13:20:01:04:c0',
               u'00:13:24:01:02:20',
               u'00:13:20:01:04:10',
               u'00:13:29:01:04:c0',
               u'00:13:22:01:04:c0',
               u'00:13:27:01:04:c0',
               u'00:13:28:01:04:c0',
               u'00:13:20:01:02:80',
               u'00:13:21:01:04:40',
               u'00:13:22:01:02:80',
               u'00:13:27:01:02:80',
               u'00:13:27:01:04:40',
               u'00:13:29:01:02:80',
               u'00:13:26:01:04:40',
               u'00:13:24:01:04:40',
               u'00:13:28:01:04:40',
               u'00:13:26:01:04:f0',
               u'00:13:26:01:03:80',
               u'00:13:29:01:02:c0',
               u'00:13:27:01:04:60',
               u'00:13:22:01:04:60',
               u'00:13:25:01:02:c0',
               u'00:13:22:01:02:c0',
               u'00:13:29:01:04:60',
               u'00:13:27:01:03:80',
               u'00:13:20:01:02:c0',
               u'00:13:22:01:03:80',
               u'00:13:24:01:02:40',
               u'00:13:29:01:02:40',
               u'00:13:20:01:04:20',
               u'00:13:25:01:04:20',
               u'00:13:25:01:02:40',
               u'00:13:22:01:02:40',
               u'00:13:22:01:04:20',
               u'00:13:26:01:02:40',
               u'00:13:24:01:04:20',
               u'00:13:27:01:02:40',
               u'00:13:27:01:03:30',
               u'00:13:28:01:03:30',
               u'00:13:29:01:03:30',
               u'00:13:20:01:03:30',
               u'00:13:26:01:03:30',
               u'00:13:21:01:03:30',
               u'00:13:22:01:03:30',
               u'00:13:25:01:03:30',
               u'00:13:21:01:03:60',
               u'00:13:24:01:03:30',
               u'00:24:82:0a:ca:f0',
               u'00:13:25:01:03:60',
               u'00:13:22:01:02:90',
               u'00:13:28:01:02:60',
               u'00:13:21:01:04:30',
               u'00:13:26:01:03:70',
               u'00:13:24:01:03:40',
               u'00:13:22:01:03:70',
               u'00:13:29:01:03:70',
               u'00:13:27:01:03:70',
               u'00:13:24:01:03:70',
               u'00:13:28:01:03:70',
               u'00:13:21:01:03:70',
               u'00:13:24:01:04:70',
               u'00:13:27:01:04:70',
               u'00:13:22:01:02:e0',
               u'00:13:26:01:04:70',
               u'00:13:22:01:04:70',
               u'00:13:28:01:02:e0',
               u'00:13:20:01:04:70',
               u'00:13:21:01:04:70',
               u'00:13:25:01:02:e0',
               u'00:13:29:01:04:70',
               u'00:13:20:01:02:b0',
               u'00:13:21:01:04:a0',
               u'00:13:24:01:02:b0',
               u'00:13:29:01:02:b0',
               u'00:13:26:01:04:a0',
               u'00:13:27:01:04:a0',
               u'00:13:22:01:04:a0',
               u'00:13:25:01:04:a0',
               u'00:13:28:01:04:10',
               u'00:13:27:01:02:b0',
               u'00:13:21:01:02:b0',
               u'00:13:26:01:02:a0',
               u'00:13:24:01:04:10',
               u'00:13:21:01:03:80',
               u'00:13:25:01:03:80',
               u'00:13:21:01:02:c0',
               u'00:13:29:01:03:80',
               u'00:13:28:01:04:60',
               u'00:13:27:01:02:c0',
               u'00:13:24:01:03:80',
               u'00:13:25:01:04:60',
               u'00:13:20:01:03:80',
               u'00:13:28:01:02:c0',
               u'00:13:25:01:02:90',
               u'00:13:28:01:03:60',
               u'00:13:24:01:02:90',
               u'00:13:25:01:04:b0',
               u'00:13:20:01:04:b0',
               u'00:13:28:01:05:00',
               u'00:13:29:01:03:00',
               u'00:13:28:01:02:00',
               u'00:13:25:01:03:00',
               u'00:13:22:01:04:00',
               u'00:13:20:01:03:00',
               u'00:13:28:01:02:10',
               u'00:13:29:01:04:b0',
               u'00:13:21:01:04:b0']
def do_config():
    return create_zd_cli_by_ip_addr(**default_cfg)

def do_test(zdcli):
    timeout = 5
    start_time = time.time()
    duration = 8 * 60 * 60
    waiting = 4 * 60
    zdcli.do_cmd(zdcli.conf['shell_key'])
    while time.time() - start_time < duration:
        logging.info('remote_ap_cli for checking memory issue')
        for mac in ap_list:  
            try:                         
                logging.info(zdcli.do_cmd('remote_ap_cli -a %s "reboot"' % mac, timeout=timeout))
            except:
                pass                    
        logging.info('waiting for %s' % waiting)
                
        st = time.time()
        while time.time() - st<waiting:
            zdcli.do_cmd("")            
            time.sleep(5)
        
        

def do_cleanup():
    clean_up_rat_env()



def main(**kargs):
    do_test(do_config())
    do_cleanup()
