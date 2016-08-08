"""
"""
import logging
from pprint import pformat
from RuckusAutoTest.components import ZoneDirectorCLI
from RuckusAutoTest.components.lib.zdcli import debug_mode_functions as DMF

def do_config(cfg):
    tcfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin')
    tcfg.update(cfg)
    zdcli = ZoneDirectorCLI.ZoneDirectorCLI(tcfg)
    return zdcli

def do_test(zdcli):
    try:
        ap_info = DMF.get_ap_info_orderby_mac(zdcli)
        logging.info("[U.ZDCLI Result-PASS] Currently Managed APs:\n%s" % (pformat(ap_info)))
        return dict(status='PASS', ap_info=ap_info)
    except:
        import traceback
        ex = traceback.format_exc()
        ap_info_output = DMF.do_debug(zdcli, 'show ap')
        xmsg = "[U.ZDCLI Result-FAIL] Not able to get ap list. Exception:\n%s\n%s" % (ex,ap_info_output)
        logging.info(xmsg)
        return dict(status='FAIL', error=xmsg, data=ap_info_output)


def do_clean_up(zdcli):
    try:
        zdcli.close()
    except:
        pass

def main(**kwargs):
    zdcli = do_config(kwargs)
    result = do_test(zdcli)
    do_clean_up(zdcli)
    return result

