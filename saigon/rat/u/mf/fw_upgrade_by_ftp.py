"""
This tea program utilizes fw_update_cont_by_ftp to upgrade
to the build specified in control_1[mf7211_image1_cntrl.rcks].

This method is not inherient, but think fw_update_cont_by_ftp
is associated (or related) to fw_upgrade_by_ftp.
Usage:

    tea.py u.mf.fw_upgrade_by_ftp ip_addr=192.168.30.1
    tea.py u.mf.fw_upgrade_by_ftp ip_addr=192.168.30.1 host=192.168.30.10
    tea.py u.mf.fw_upgrade_by_ftp control_1=mf7211_build80_control.rcks

"""

import fw_update_cont_by_ftp as fwu

def main(**kwargs):
    (ap_x, ap_inf, mf_cfg) = fwu.do_config(kwargs)
    fwu.ap_upd1(ap_x, ap_inf, mf_cfg)
    ap_ver = ap_x.get_version()
    fwu.logging.info("AP is upgraded to version: %s" % (ap_ver))
    return ap_ver

