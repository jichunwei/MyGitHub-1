'''
Tea program for METRO ADMINISTRATOR MENU
'''
from ratenv import *
import copy
import logging
from pprint import pformat as pp
from RuckusAutoTest.components import clean_up_rat_env
from RuckusAutoTest.components.lib.mf import metro_administrator as adm
from RuckusAutoTest.components import create_metro_by_model

def get_default_cfg():
    return copy.deepcopy(default_cfg)


def do_config(cfg):

  #  default_cfg = dict(
  #      selenium_mgr = _get_se_mgr(),
  #      browser_type = 'firefox',
  #      ip_addr = '192.168.0.200',
  #      username='super',
  #      password='sp-admin',
  #      https = True,
  #  )
    a = dict(ip = '192.168.0.200')
    a.update(cfg)
    bayhai = create_metro_by_model(ip_addr=a['ip'])
    bayhai.start()
    return bayhai

    #bayhai = MetroWebUIs.MF7211WebUI(**default_cfg)

def do_test(metro):
    mf = {}
    adm.telnet_enable(metro)
    adm.ssh_enable(metro)
    adm.http_enable(metro)
    adm.allow_mgmt(metro)
    adm.limit_mgmt(metro,dict(ip1='192.168.0.10'))
    mf['ping'] = adm.ping(metro,'192.168.0.10')
    mf['trace']= adm.traceroute(metro,'192.168.0.2')
    mf['log']  = adm.admin_log(metro)
    adm.admin_log_en(metro,'192.168.0.10')
    adm.refresh(metro)

    return mf


def do_clean_up(cfg):
    clean_up_rat_env()


def main(**kwa):
    metro = do_config(kwa)
    res = do_test(metro)
    logging.info(pp(res))

    return res

