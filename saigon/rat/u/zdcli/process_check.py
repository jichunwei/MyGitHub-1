'''
Checking stamgr | apmgr daemon, make sure PID is not change if doesn't do 
restart/reboot.
Created on Feb 15, 2011
@author: root

How To:
    python tea.py u.zdcli.process_check
'''
import time
import logging

from RuckusAutoTest.components import (create_zd_cli_by_ip_addr,clean_up_rat_env)
from RuckusAutoTest.components.lib.zdcli import process_mgr

default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin', shell_key = '!v54! CKQpcGkLBgVbYHWieLU9Y24SPpAeirqV')

def do_config():
    return create_zd_cli_by_ip_addr(**default_cfg)

def do_test(zdcli):
    duration = 10 * 60
    interval = 30
    st = time.time()
    #orignal
    stamgrlist = process_mgr.get_stamgr_status(zdcli)
    apmgrlist = process_mgr.get_apmgr_status(zdcli)
    weblist = process_mgr.get_webs_status(zdcli)        
    while time.time()-st<duration:
        time.sleep(interval)
        try:
            s2 = process_mgr.get_stamgr_status(zdcli)
            assert(s2!=None)
            a2 = process_mgr.get_apmgr_status(zdcli)
            assert(a2!=None)                   
            w2 = process_mgr.get_webs_status(zdcli)
            assert(w2!=None)         
        except Exception, e:
            logging.error(e)
            continue
        (res, info) = process_mgr.diff_pid_status(stamgrlist, s2)
        logging.info('========stamgr=============') 
        if res:            
            logging.info(info)
        else:
            logging.error(info)

        (res, info) = process_mgr.chk_process_status_ok(s2)
        if not res:
            logging.error(info)
        else:
            logging.info(info)
                    
        (res, info) = process_mgr.diff_pid_status(apmgrlist, a2)
        logging.info('========apmgr=============')
        if res:            
            logging.info(info)
        else:
            logging.error(info)

        (res, info) = process_mgr.chk_process_status_ok(a2)
        if not res:
            logging.error(info)
        else:
            logging.info(info)
                    
        (res, info) = process_mgr.diff_pid_status(weblist, w2)
        logging.info('========webs=============')
        if res:            
            logging.info(info)
        else:
            logging.error(info)
                         
        (res, info) = process_mgr.chk_process_status_ok(w2)
        if not res:
            logging.error(info)
        else:
            logging.info(info)
                            
def do_cleanup():
    clean_up_rat_env()

def main(**kwargs):
    do_test(do_config())
    do_cleanup()
