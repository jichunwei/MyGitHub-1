
'''
Created on Oct 18, 2010

@author: webber.lin
Purpose:

Remote restore FM database via test engine.
This tea program will execute auto_install_fm.py remotely and install FM


Example: (no keyword arguments need)

tea.py u.scaling.fm_install

'''


import time
from RuckusAutoTest.common.Ratutils import send_mail

from u.scaling.lib.common_remote_control import installFM, checkFMIso,pingFM

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
        res2 = installFM(res['fm_obj'],cfg['iso'])
        res.update(res2)
    
    print "####################################################################"
    print "[info] Need to wait for 10 minutes for reconnect AP/ZDs to FM server"
    print "####################################################################"
    time.sleep(600)
    return res


def do_clean_up(cfg):
    #it is all background job, so no need to call clean_rat_env()
    pass


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)
    send_mail("172.16.100.20", tcfg['email'], "RAT <webber.lin@ruckuswireless.com>", "FM is installed successfully", "Result: %s" % res )
    return res

