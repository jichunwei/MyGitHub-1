'''
Created on Jan 20, 2011

@author: lab
'''
import logging
import time

from contrib.ping import ping_win32

def do_config():
    pass

def do_test(ipaddr='192.168.0.2'):
    duration = 8 * 60 * 60
    wait_for = 2
    st = time.time()
    while time.time() - st < duration:
        logging.info(ping_win32(ipaddr, length=1024))
        time.sleep(wait_for)


def do_cleanup():
    pass


def main(**kwargs):
    do_test()