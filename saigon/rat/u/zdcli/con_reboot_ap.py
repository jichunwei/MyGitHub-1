'''
Created on Jan 20, 2011
@author: lab
concurrency reboot AP
'''

import logging
import time

from threading import Thread

from ip import iplist
from AP import AP


class Reboot(Thread):
    def __init__(self, ip):                
        self.ip = ip
        Thread.__init__(self, name=ip)
            
    def run(self):
        try:
            logging.info('Handle ap[%s]' % self.ip)
            ap = AP(self.ip)
            ap.login('admin', 'admin')
            ap.cmd('reboot')
            logging.info('Reboot ap[%s] compeletely' % self.ip)
        except Exception, e:
            logging.info(e)

def do_config():
    pass
#    return create_zd_cli_by_ip_addr(**default_cfg)


def do_test():
    start_time = time.time()
    duration = 8 * 60 * 60
    waiting = 8 * 60
    while time.time() - start_time<duration:
        for ip in iplist:
            Reboot(ip).start()
            time.sleep(0.2)
        logging.info('pending...')
        time.sleep(waiting)
            
def do_cleanup():
    pass


def main(**kwargs):
    do_test()

