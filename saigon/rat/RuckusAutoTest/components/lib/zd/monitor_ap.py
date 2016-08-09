import logging
import time

from RuckusAutoTest.components.lib.zd import control_zd as control_zd
from RuckusAutoTest.common import lib_Constant as constant

LOCATORS_ADMIN_DIAG  = {
    'loc_ap_sys_info':r"//img[@id='gen-support-apsummary-0']",
    'search_box':r"//table[@id='apsummary']//span[@class='other-act']/input",
}

save_to = save_to = constant.save_to

def save_ap_sys_info(zd,ap_mac):
    zd.navigate_to(zd.MONITOR, zd.MONITOR_ACCESS_POINTS)
    button = LOCATORS_ADMIN_DIAG['loc_ap_sys_info']
    box = LOCATORS_ADMIN_DIAG['search_box']
    
    zd._fill_search_txt(box, ap_mac)#Chico, 2015-3-5, sometimes exception reported, ZF-12268
    
    file_path = control_zd.download_single_file(zd, button, filename_re='.+.txt', save_to=save_to)
    logging.debug('The current file save at %s' % file_path)
    zd.s.type_text(box,'')
    if not file_path:
        logging.error("save file fail! the file is empty")
        return False
    return True