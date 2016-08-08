'''
Tea program to test METRO STATUS GROUP MENU , including Device, Internet, System, Wireless
'''
import ratenv
import copy
import logging
from pprint import pformat as pp
from RuckusAutoTest.components import create_metro_by_model
from RuckusAutoTest.components import clean_up_rat_env
from RuckusAutoTest.components.resources import MetroWebUIResource
from RuckusAutoTest.components import MetroWebUIs
from RuckusAutoTest.components.lib.mf import metro_status as stat

def get_default_cfg():
    return copy.deepcopy(default_cfg)

def do_config(cfg):
    a = dict(ip = '192.168.0.200')
    a.update(cfg)
    bayhai = create_metro_by_model(a['ip'])
    bayhai.start()
    return bayhai

def do_test(cfg):
    mf = {}
    mf['device']    = stat.get_device_status(cfg)
    mf['air']       = stat.get_air_quality()
    mf['internets'] = stat.get_internet_status()
    mf['system']    = stat.get_system_status()
    mf['common']    = stat.get_wireless_common_status()
    mf['wireless']  = stat.get_wireless_status(0)
    mf['wireless']  = stat.get_wireless_status(1)
    mf['wireless']  = stat.get_wireless_status(2)


    return mf

def do_clean_up(cfg):
    clean_up_rat_env()

def main(**kwa):
    abc = do_config(kwa)
    res = do_test(abc)
   # logging.info(pp(res))
    do_clean_up(abc)
    return res

