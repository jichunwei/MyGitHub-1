"""
This tea program continously "fw update" the mf7211 to validate the number of updating the flash until it fail.

Pre-requirement:

    ftp server:
        [1] ftp user with user/password: apfwupdate/apfwupdate
        [2] default ftp host is 192.168.30.10, overwritten by arg host
        [3] ftp user apfwupdate's home directory containing ap control files and their images
            image1 control file is: mf7211_image1_cntrl.rcks
            image2 control file is: mf7211_image2_cntrl.rcks

            The image file has format:

                [rcks_fw.main]
                0.0.0.0
                7211_4.5.0.0.56_uImage
                2705471

            where 7211_4.5.0.0.56_uImage is mf7211 image file name, and
            2705471 is the actual byte size of the image file.

        [4] for 3CDaemon ftp server, it can only support up to 3 ftp sessions at one time.

    AP, the dut:
        [1] default ip is 192.168.30.251, overwritten by arg ip_addr
        [2] enable AP's telnet. Although script will enable AP's telnet after
            ssh. In some instance the ssh connection can not be established.
Usage:

    tea.py u.fm.fw_update_cont_by_ftp ip_addr=192.168.30.245
    tea.py u.fm.fw_update_cont_by_ftp ip_addr=192.168.30.245 update_timeout=420
    tea.py u.fm.fw_update_cont_by_ftp ip_addr=192.168.30.245 username=superx password=sx-admin
    tea.py u.fm.fw_update_cont_by_ftp ip_addr=192.168.30.245 host=192.168.30.32
    tea.py u.fm.fw_update_cont_by_ftp control_1=mf7211_image1_cntrl.rcks control_2=mf7211_image1_cntrl.rcks

    # If arg ctrl_list presented, it overwries control_1 and control_2
    tea.py u.fm.fw_update_cont_by_ftp ctrl_list=['image1_cntrl.rcks','image2_cntrl.rcks','image3_cntrl.rcks']

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
    logging.info("\n###\n### FW UPDATE by FTP thru LAN #%d\n%s" % (xstep['c'],bline))

def show_fwinfo(ap_x):
    fwinfo = ap_x.get_fw_upgrade_setting()
    logging.info(pformat(fwinfo))

def ap_init(cfg):
    mf_cfg = dict(ip_addr='192.168.30.251',username='super',password='sp-admin',
                  host='192.168.30.10',host_user='apfwupdate',host_password='apfwupdate',
                  update_timeout=360,
                  control_1='mf7211_image1_cntrl.rcks',
                  control_2='mf7211_image2_cntrl.rcks',
                  pausedict=dict(after_reboot=10))
    mf_cfg.update(cfg)
    ap_x = RuckusAP.RuckusAP(mf_cfg)
    ap_inf['0_c'] = ap_x.get_fw_upgrade_setting()
    ap_inf['0_v'] = ap_x.get_version()
    logging.info(pformat(ap_inf))
    return (ap_x,ap_inf,mf_cfg)

def ap_upd1(ap_x, ap_inf,my_cfg):
    pr_step()
    ap_inf['1_v'] = ap_x.get_version()
    ap_inf['1_c'] = dict(host=my_cfg['host'],
                         proto='ftp', auto=False,
                         user=my_cfg['host_user'], password=my_cfg['host_password'],
                         control=my_cfg['control_1'])
    ap_x.change_fw_setting(ap_inf['1_c'])
    ap_inf['1_cs'] = ap_x.get_fw_upgrade_setting()
    logging.info(pformat(ap_inf['1_cs']))
    #ap_x.upgrade_sw_ap(None)
    ap_x.update_ap_fw(timeout=my_cfg['update_timeout'])
    ap_inf['1_vs'] = ap_x.get_version()
    logging.info(pformat(ap_inf))
    #logging.info(ap_x.cmd('fw show all', return_list=False))

def ap_upd2(ap_x, ap_inf,my_cfg):
    pr_step()
    ap_inf['2_v'] = ap_x.get_version()
    ap_inf['2_c'] = dict(host=my_cfg['host'],
                         proto='ftp', auto=False,
                         user=my_cfg['host_user'], password=my_cfg['host_password'],
                         control=my_cfg['control_2'])
    ap_x.change_fw_setting(ap_inf['2_c'])
    ap_inf['2_cs'] = ap_x.get_fw_upgrade_setting()
    logging.info(pformat(ap_inf['2_cs']))
    #ap_x.upgrade_sw_ap(None)
    ap_x.update_ap_fw(timeout=my_cfg['update_timeout'])
    ap_inf['2_vs'] = ap_x.get_version()
    logging.info(pformat(ap_inf))
    #logging.info(ap_x.cmd('fw show all', return_list=False))

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
ap_x = None
ap_inf = dict()
mf_cfg = dict()

def do_config(cfg):
    return ap_init(cfg)

def do_test_from_list(ap_x, ap_inf, my_cfg, control_list=[]):
    step = 0
    n_control=len(control_list)
    while (1):    
        clidx = step / n_control
        my_cfg['control_1'] = control_list[clidx]
        ap_upd1(ap_x, ap_inf, my_cfg)
        if take_break(): break
    return

def do_test_default(ap_x, ap_inf, my_cfg):
    while (1):    
        ap_upd1(ap_x, ap_inf, my_cfg)
        if take_break(): break
        ap_upd2(ap_x, ap_inf, my_cfg)
        if take_break(): break
    return

def do_test(ap_x, ap_inf, my_cfg):
    if my_cfg.has_key('ctrl_list'):
        control_list = my_cfg.pop('ctrl_list')
        do_test_from_list(ap_x, ap_inf, my_cfg, control_list)
    else:
        do_test_default(ap_x, ap_inf, mf_cfg)

def do_clean_up(ap_x, ap_inf, mf_cfg):
    return

def main(**kwargs):
    (ap_x, ap_inf, mf_cfg) = do_config(kwargs)
    do_test(ap_x, ap_inf, mf_cfg)
    do_clean_up(ap_x, ap_inf, mf_cfg)


