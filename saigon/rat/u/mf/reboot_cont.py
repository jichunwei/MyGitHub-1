"""
This tea program continously reboot the AP until it fail.
This test validates that the AP locked problem is not the reboot command, but other issues.

Usage:

    tea.py u.fm.reboot_cont ip_addr=192.168.30.245 pausedict=dict(after_reboot=10)
    tea.py u.fm.reboot_cont ip_addr=192.168.30.245 host=192.168.30.32

"""
from RuckusAutoTest.components import RuckusAP
from pprint import pprint, pformat
import os
import pdb
import logging

STOP_TESTING_NOW='MF_ACTION_STOP'
HALT_TESTING_NOW='MF_ACTION_HALT'

xstep = dict(c=0)
def pr_step():
    bline = '#' * 76
    xstep['c'] += 1
    logging.info("\n###\n### REBOOT #%d\n%s" % (xstep['c'],bline))

def ap_init(cfg):
    mf_cfg = dict(ip_addr='192.168.30.251',username='super',password='sp-admin',
                  exit_on_pingable=True,
                  pausedict=dict(after_reboot=10))
    mf_cfg.update(cfg)
    ap_x = RuckusAP.RuckusAP(mf_cfg)
    ap_inf = dict()
    fw_cfg = dict(auto=False)
    ap_x.change_fw_setting(fw_cfg)
    ap_inf['fw_settings'] = ap_x.get_fw_upgrade_setting()
    ap_inf['version'] = ap_x.get_version()
    logging.info(pformat(ap_inf))
    return (ap_x,ap_inf,mf_cfg)

def ap_reboot(ap_x,ap_inf,my_cfg):
    pr_step()
    ap_x.reboot(exit_on_pingable=my_cfg['exit_on_pingable'])
    ap_inf['ver_reboot'] = ap_x.get_version()
    logging.info(pformat(ap_inf))

def take_break():
    if os.path.exists(HALT_TESTING_NOW):
        import pdb
        pdb.set_trace()
    if os.path.exists(STOP_TESTING_NOW):
        return 1
    return 0

##
## tea program structure
##
def do_config(cfg):
    return ap_init(cfg)

def do_test(ap_x, ap_inf, my_cfg):
    while (1):    
        ap_reboot(ap_x, ap_inf, my_cfg)
        if take_break(): break

def do_clean_up(ap_x, ap_inf, my_cfg):
    return

def main(**kwargs):
    (ap_x, ap_inf, mf_cfg) = do_config(kwargs)
    do_test(ap_x, ap_inf, mf_cfg)
    do_clean_up(ap_x, ap_inf, mf_cfg)


