'''
Tea program to test METRO MAINTENANCE GROUP MENU
'''
import ratenv
import copy
import logging
from pprint import pformat as pp
from RuckusAutoTest.components import create_metro_by_model
from RuckusAutoTest.components import clean_up_rat_env
from RuckusAutoTest.components.resources import MetroWebUIResource
from RuckusAutoTest.components import MetroWebUIs
from RuckusAutoTest.components.lib.mf import metro_maintenance as ma

def get_default_cfg():
    return copy.deepcopy(default_cfg)

def do_config(cfg):
    a = dict(ip = '192.168.0.200')
    a.update(cfg)
    bayhai = create_metro_by_model(ip_addr=a['ip'])
    bayhai.start()
    return bayhai

def do_test(metro):
    mf = {}
    #ma.auto_upgrade_enable(metro)
    #ma.auto_upgrade_check_interval(metro,60)
    #ma.reboot_time_after_upgrade(metro,12)
    mf['log'] = ma.get_current_log(metro)
    ma.upgrade_ftp(metro,imagefile='mf7211_56_cntrl.rcks')
    ma.reboot(metro)
    
    return mf

def do_clean_up(cfg):
    clean_up_rat_env()

def main(**kwa):
    metro = do_config(kwa)
    res = do_test(metro)
   # logging.info(pp(res))
    do_clean_up(metro)
    return res

