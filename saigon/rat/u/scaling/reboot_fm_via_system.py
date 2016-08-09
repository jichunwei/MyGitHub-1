'''
Created on Oct 22, 2010

purpose: 

this tea program is to reboot FM server 10 times in 8 hours via telnet

these two program must be stored in the same folder

Example: 
tea.py u.scaling.reboot_fm_via_system linux_srv_ip=172.17.18.31 user=root password=!v54!scale
tea.py u.scaling.reboot_fm_via_system linux_srv_ip=192.168.30.252 user=root password=lab4man1


@author: webber.lin
'''

import time

import logging
from RuckusAutoTest.common.Ratutils import send_mail
from pprint import pformat
from u.scaling.lib.scaling_navigation import nav_to_dashboard
from u.scaling.lib.dashboard_tables import (get_num_of_connectedZD,\
                                            get_num_of_connectedAP,\
                                            get_num_of_disconnectedAP,\
                                            get_num_of_connectedAP_in_1day,\
                                            get_num_of_connectedAP_in_2days,\
                                            get_num_of_clients_from_ap_table,\
                                            )
from RuckusAutoTest.components import create_fm_by_ip_addr,clean_up_rat_env

from u.scaling.lib.common_remote_control import (pingFM,\
                                                 createLinuxPc,\
                                                 restartFMserver,\
                                                 rebootLinuxPc,\
                                                 loginLinuxPc,)


#self defined VAR/CONSTANT


WAIT_FM_BOOTUP=180
 
def timer_minute(minute=1):
    logging.debug('Waiting Time is set up to %d minutes' % minute)
    time.sleep(60*minute)

def getTimeInterval(hours=8,times=10):
    return hours * 60 / times



    
def do_config(cfg):
    p = dict(
        linux_srv_ip = '172.17.18.31',
        user = 'root',
        password = '!v54!scale',
        root_password = '!v54!scale',
        hours=8,
        times=10,
        email='raiki.huang@ruckuswireless.com'
    )
    p.update(cfg)
    p['fm_terminal'] = createLinuxPc(cfg['linux_srv_ip'])
    p['time_interval'] = getTimeInterval(p['hours'],p['times'])
    
    
    
    
    logging.info('[do_config] configure successfully.\n %s' % pformat(p))
    return p


def do_test(cfg):
    try:
        #1. reboot 10 times in 8 hours
        for count in range(cfg['times']):
            #import pdb
            #pdb.set_trace()
            if not pingFM(cfg['linux_srv_ip']): #FM must be pingable, then do following tests
                
                #frontend check
                logging.info('launch FM WebUI and verify connected Devices')
                
                #create fm web gui and stay at dashboard page
                cfg['fm_web'] = create_fm_by_ip_addr(cfg['linux_srv_ip'])
                nav_to_dashboard(cfg['fm_web'])
                
                #grab from ap and zd tables in dashboard page
                connected_ap = get_num_of_connectedAP(cfg['fm_web'])
                connected_zd = get_num_of_connectedZD(cfg['fm_web'])
                disconnected_ap = get_num_of_disconnectedAP(cfg['fm_web'])
                connected_ap_in_1day = get_num_of_connectedAP_in_1day(cfg['fm_web'])
                connected_ap_in_2days = get_num_of_connectedAP_in_2days(cfg['fm_web'])
                clients = get_num_of_clients_from_ap_table(cfg['fm_web'])
                logging.info('\nZD devices table:\nConnectedZD: %s' % connected_zd)
                logging.info('\nAP devices table:\nconnectedAP: %s\t disconnected: %s\nseen in 1 day: %s\tseen in 1 day: %s\nClients: %s' %\
                             (connected_ap,disconnected_ap,connected_ap_in_1day,connected_ap_in_2days,clients))
                logging.info('Reboot in 5 seconds (Cycle: %s)' % str(count+1))
                time.sleep(5)
                
                
                res = rebootLinuxPc(cfg['fm_terminal'])
                logging.debug('Result:\n%s' % res)
                #after reboot linux, fm_obj is totally gone
                clean_up_rat_env()
                
                
                
                #Wait_FM_bootup
                logging.debug('Wait for 3 minutes for FM server up and running')
                time.sleep(WAIT_FM_BOOTUP)
                
                loginLinuxPc(cfg['fm_terminal'])
                logging.info('Wait for %s minutes to reboot' % str(cfg['time_interval']-WAIT_FM_BOOTUP/60))
                timer_minute(cfg['time_interval']-WAIT_FM_BOOTUP/60) #wait for 48 minutes
        
        return dict(result='PASS',message='reboot FM server %d times successfully' % cfg['times'])
    except:
        return dict(result='FAIL',message='Unable to reboot FM server %d times in %d hours' % (cfg['times'],cfg['hours']))            
    return res


def do_clean_up(cfg):
    #didn't open any selenium obj, so keep empty in this function.
    pass


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)
    send_mail("172.16.100.20", tcfg['email'], "RAT <webber.lin@ruckuswireless.com>", "FM database is restored successfully", "Result: %s" % res )
    return res
