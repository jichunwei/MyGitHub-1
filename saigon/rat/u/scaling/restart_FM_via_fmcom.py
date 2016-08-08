'''
Created on Oct 28, 2010

@author: webber.lin
'''

'''
Created on Oct 22, 2010

purpose: 

this tea program is to reboot FM server 10 times in 8 hours via telnet

these two program must be stored in the same folder

Example: tea.py u.scaling.scpFMbuild 


@author: webber.lin
'''

import time

import logging
from RuckusAutoTest.common.Ratutils import send_mail
from pprint import pformat

from u.scaling.lib.scaling_navigation import nav_to_dashboard
from u.scaling.lib.dashboard_tables import (get_num_of_connectedZD,\
                                            get_num_of_connectedAP,\
                                            get_all_stand_APs_fromAP_device_view_table,\
                                            get_num_of_disconnectedAP,\
                                            get_num_of_connectedAP_in_1day,\
                                            get_num_of_connectedAP_in_2days,\
                                            get_num_of_clients_from_ap_table,\
                                            )

from RuckusAutoTest.components import create_fm_by_ip_addr
from u.scaling.lib.common_remote_control import pingFM, createLinuxPc,restartFMserver,rebootLinuxPc


#self defined VAR/CONSTANT



 
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
    p['fm_terminal'] = createLinuxPc(cfg['linux_srv_ip'],cfg['user'],cfg['password'])
    p['time_interval'] = getTimeInterval(p['hours'],p['times'])
    p['fm_web'] = create_fm_by_ip_addr(p['linux_srv_ip'])
    logging.info('[do_config] configure successfully.\n %s \n\n' % pformat(p))
    return p


def do_test(cfg):
    try:
        #1. reboot 10 times in 8 hours
        for count in range(cfg['times']):
            #import pdb
            #pdb.set_trace()
            if not pingFM(cfg['linux_srv_ip']): #FM must be pingable, then do following tests
                
                
                #----------------------------------------------------------
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
                logging.info('Restart FM server in 5 seconds (Cycle: %s)' % str(count+1))
                time.sleep(5)
                res = restartFMserver(cfg['fm_terminal'])
                #----------------------------------------------------------
                # add 2 verifications after reboot FM
                # check fm status from backend
                # check fm status from frontend web gui
                logging.debug('Result:\n%s' % res)
                logging.info('Wait for %d minutes to reboot' % cfg['time_interval'])
                timer_minute(cfg['time_interval']) #wait for 48 minutes
        return dict(result='PASS',message='restart FM services successfully for %d times' % cfg['times'])
    except:
        return dict(result='FAIL',message='Unable to restart FM services %d times in %d hours' % (cfg['times'],cfg['hours']))            
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
