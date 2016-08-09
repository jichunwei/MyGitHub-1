'''
Created on Oct 18, 2010

@author: webber.lin
Purpose:

Remote restore FM database via test engine.
This tea program will call auto_install_fm.py and restore FM database


Example:
tea.py u.scaling.fm_db_restore

'''


import time
import os
import logging
from RuckusAutoTest.common.Ratutils import send_mail

from u.scaling.lib.common_remote_control import restoreFMDB, checkFMIso,pingFM

#self defined VAR/CONSTANT


ISO='FM_9.0.0.0.126.20100719_0004.iso'#Exact FM build name
 
    
def do_config(cfg):
    p = dict(
        linux_srv_ip = '192.168.30.252',
        user = 'lab',
        password = 'lab4man1',
        root_password = 'lab4man1',
        iso=ISO,
        email='webber.lin@ruckuswireless.com'
    )
    p.update(cfg)
    
    return p


def do_test(cfg):
    if not pingFM(cfg['linux_srv_ip']): #FM must be pingable, then do following tests
        res = checkFMIso(cfg['iso'],cfg['linux_srv_ip'])
        res2 = restoreFMDB(res['fm_obj'],cfg['iso'])
        res.update(res2)
    
    print "####################################################################"
    print "[info] Need to wait for 10 minutes for reconnect AP/ZDs to FM server"
    print "####################################################################"
    time.sleep(180)
    return res


def do_clean_up(cfg):
    pass


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)
    send_mail("172.16.100.20", tcfg['email'], "RAT <webber.lin@ruckuswireless.com>", "FM database is restored successfully", "Result: %s" % res )
    return res
