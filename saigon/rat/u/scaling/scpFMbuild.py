'''
Created on Oct 19, 2010

purpose: 
this tea program is 
to copy FM build from test 
engine to FM linux server.

this tea program needs to be run with portable program
winscp.com and winscp.exe

these two program must be stored in the same folder

Example: tea.py u.scaling.scpFMbuild 


@author: webber.lin
'''


import time
from RuckusAutoTest.common.Ratutils import send_mail
from pprint import pformat
from u.scaling.lib.common_remote_control import checkFMIso,pingFM,scpBuildfromTEtoFM

#self defined VAR/CONSTANT


ISO='FM_9.0.0.0.126.20100719_0004.iso'#Exact FM build name
 
    
def do_config(cfg):
    
    p=dict(     
                session='FM',\
                winscp=r'"\Documents and Settings\lab\Desktop\WinSCP.com"', \
                source='a.test',\
                source_dir=r'\Integration\demo_saigon_56496\firmwares\fm_iso',\
                target_dir='/tmp',\
                username='root',\
                password='lab4man1',\
                ip_addr='192.168.30.252',\
                email='webber.lin@ruckuswireless.com',\
                #common fm server no finger print
                hostkey='',\
                #scaling machine:172.17.18.31 need ssh rsa finger print
                #hostkey='ssh-rsa 2048 16:83:a4:96:31:04:39:c2:c5:3a:53:55:6c:05:df:6a',\
                )
    p.update(cfg)
    
    return p


def do_test(cfg):
    if not pingFM(cfg['ip_addr']): #FM must be pingable, then do following tests
        res = scpBuildfromTEtoFM(cfg)

    return res


def do_clean_up():
    #it is all background job, so no need to call clean_rat_env()
    pass


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up()
    #send_mail("172.16.100.20", tcfg['email'], "RAT <webber.lin@ruckuswireless.com>", "Copy FM build to FM server successfully", "Result: %s" % res )
    return res

