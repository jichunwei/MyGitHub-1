'''
Created on Aug 24, 2010

@author: webber.lin

Purpose: restore golden database to ensure 
         database won't affect FM regression testing.

Steps:  1. telnet to FM server. (this step need to enable telnet on FM server)
        2. Running auto_install_FM script on FM server remotely
        3. Shutdown FM
        4. Restore Database
        5. Set up timeout 10 minutes and wait for AP/ZD connection back to FM
        
        This tea program must be run in a batch file.
        
batch File: 

Environment Setup: 

1. FM server:
2. Test Engine:


How-To run this tea program:
tea.py u.scaling.fmdb_control linux_srv_ip=192.168.30.252 iso=FM_9.0.0.0.126.20100719_0004.iso email=webber.lin@ruckuswireless.com

'''


import time
import os
from RuckusAutoTest.common.Ratutils import send_mail
from RuckusAutoTest.components.LinuxPC import LinuxPC as LP


#self defined VAR/CONSTANT

PORT='22' #telnet



def restoreFMDB(fm_obj,iso):
    ''' This method is telnet to FM and restore db remotely on FM server
        After telnet to FM, run the below command:
        python auto_install_FM.py FM_9.0.0.0.126.20100719_0004.iso backup
    '''
    try:
        fm_obj.login()
        cmd_text_list = ['cd /tmp','python auto_install_FM.py %s restore' % iso]
        for cmd in cmd_text_list:
            print "[info] Command: %s" % cmd
            fm_obj.do_cmd(cmd)
            time.sleep(3)
 
        res = dict(result='PASS', message='Restore FM database successfully')
    except Exception, e:
        res = dict(
            result='ERROR', message='Cannot restore FM database Error: %s' % e.__str__()
        )

    return res

def pingFM(fm_ip='192.168.30.252'):
    '''Make sure FM is pingable and alive!!'''
    err=os.system("ping 192.168.30.252")
    #status:
    # ping success: 0
    # ping failed: 1
    # ping unknown: 1
    return err    
            
    
def checkIso(isoname,fm_ip):
    ''' Ensure Iso is already moved to /tmp'''
    fm = LP(dict(ip_addr=fm_ip))
    try:
        
        cmd = 'ls /tmp/%s' % isoname
        fm.do_cmd(cmd)
        res = dict(iso_message='iso: %s is existed' % isoname, fm_obj=fm)
    except Exception, e:
        res = dict(iso_message='iso: %s is not existed and Error: %s' %(isoname,e.__str__()),fm_obj=fm)
    return res    
    
def do_config(cfg):
    p = dict(
        linux_srv_ip = '192.168.30.252',
        user = 'lab',
        password = 'lab4man1',
        root_password = 'lab4man1',
        iso='FM_9.0.0.0.126.20100719_0004.iso',
        email='webber.lin@ruckuswireless.com'
    )
    p.update(cfg)
    
    return p


def do_test(cfg):
    if not pingFM(cfg['linux_srv_ip']): #FM is pingable
        res = checkIso(cfg['iso'],cfg['linux_srv_ip'])
        res2 = restoreFMDB(res['fm_obj'],cfg['iso'])
        res.update(res2)
    time.sleep(600)
    print "####################################################################"
    print "[info] Need to wait for 10 minutes for reconnect AP/ZDs to FM server"
    print "####################################################################"
    return res


def do_clean_up(cfg):
    pass


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)
    send_mail("172.16.100.20", tcfg['email'], "RAT <webber.lin@ruckuswireless.com>", "FM database is restored successfully", "Result: %s" % res )
    return res
