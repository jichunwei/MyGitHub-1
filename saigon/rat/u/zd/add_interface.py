'''
Created on 2010-11-08

@author: anhtt
tea.py add_interface te_root=u.zd en_mgmt_interface=True add_if_ip='192.168.2.1' if_mask='255.255.255.0' if_vlan=''
'''
import logging
import time

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)
from RuckusAutoTest.components.lib.zd import add_mgmt_interface as add_if
from RuckusAutoTest.common.utils import compare_dict

default_cfg = dict(ip_addr = '192.168.30.247', username = 'admin', password = 'admin')
def do_config(**kwargs):
    args = dict(en_mgmt_interface=True,
                add_if_ip='192.168.2.1',
                if_mask='255.255.255.0',
                if_vlan='')
    return args.update(kwargs)

def do_test(zd, cfg):
    add_if.enable_mgmt_interface(zd, cfg)
    time.sleep(15)
    result = add_if.get_mgmt_interface(zd)
    errmsg = compare_dict(cfg, result, tied_compare=False)
    if self.errmsg:
       return ('FAIL', "The configuration information cannot apply to ZD")

    return ('PASS', "Add interface successfully")

def do_clean_up():
    clean_up_rat_env()

def main(**kwargs):
    zd = create_zd_by_ip_addr(**default_cfg)
    try:
        cfg = do_config(**kwargs)
        res = do_test(zd, cfg)
        do_clean_up()
        return res
    finally:
        pass

if __name__ == '__main__':
    kwargs = dict()
    main(**kwargs)

