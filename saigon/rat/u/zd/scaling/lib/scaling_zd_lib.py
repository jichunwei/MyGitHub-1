'''
Extract those common APIs which are relative with ZD. 
Created on 2010-2-9
@author: cwang@ruckuswireless.com
'''
import logging
import re
import time

from RuckusAutoTest.common.DialogHandler  import (DialogManager, 
                                                  StandardDialog
                                                  )
from RuckusAutoTest.common.Ratutils  import ping
from RuckusAutoTest.components.lib.zd import access_points_zd as AP



def resolve_verify_all_aps(zd):
    list_of_connected_aps = list()
    
    apInfos = zd.get_all_ap_info()
    
    for ap in apInfos:
        if ap['status'].lower().startswith(u"connected"):
            list_of_connected_aps.append(ap)
    if len(list_of_connected_aps) == 0:
        raise Exception("No AP connected")      
    return list_of_connected_aps

def upgrade_sw(zd, img_path):

        """ Upgrade the Zone Director to the image specified by the img_path path.

        Make sure that all connected APs are upgraded and connected successfully after upgrading.
        After upgrading, this method will navigate to the ZD's URL without logging in
        """
#        zd._login()
#        zd._navigateTo(zd.ADMIN, zd.ADMIN_UPGRADE)
        zd.navigate_to(zd.ADMIN, zd.ADMIN_UPGRADE)

        upgrade_file_textbox = zd.info['loc_admin_browse_file_button']
        
        if not zd.s.check_element_present(upgrade_file_textbox):
            raise Exception("Element %s not found" % upgrade_file_textbox)

        if zd.browser_type == "ie":
           
            dlg = StandardDialog(StandardDialog.IE_CHOOSE_FILE_DLG, img_path)
            manager = DialogManager()
            manager.addDialog(dlg)
            manager.start()
            zd.s.click(upgrade_file_textbox)
            manager.join(10)
            manager.shutdown()
        else:
            if not zd._safeType(upgrade_file_textbox, img_path):
                raise Exception("Can not set value %s to the locator %s" % (img_path, upgrade_file_textbox))
#        import pdb
#        pdb.set_trace()
        logging.info("Wait for build to be fully uploaded. This process takes some seconds. Please wait...")
        
        #try to enfore upgrading
        
        perform_upgrade_button = zd.info['loc_admin_perform_upgrd_button']
        error_upgrade_span = zd.info['loc_admin_error_upgrade_span']
            
        # Bypass the confirmation to backup the config file which happens on ZD7.1
        zd.s.choose_cancel_on_next_confirmation()

        t0 = time.time()
        time_out = 60
        while True:
            if zd.s.is_element_present(error_upgrade_span) and zd.s.is_visible(error_upgrade_span):
                msg = zd.s.get_text(error_upgrade_span)
                logging.warning(msg)
                
            if zd.s.is_element_present(perform_upgrade_button) and zd.s.is_visible(perform_upgrade_button):
                break
            if time.time() - t0 > time_out:
                raise Exception("The upgrade process was not completed after %s seconds" % time_out)
            time.sleep(2)
        # Ensure that the confirmation is removed if it does exist
        if zd.s.is_confirmation_present():
            logging.info("Got confirmation: %s" % zd.s.get_confirmation())

        
        if zd._checkElementPresent("//input[@id='upgrade_errorinput_1']"):
            zd._click("//input[@id='upgrade_errorinput_1']")
        time.sleep(1)
            
        # Bypass the confirmation to perform upgrading
        zd.s.choose_ok_on_next_confirmation()
        zd._click(perform_upgrade_button)
        if zd.s.is_confirmation_present():
            zd.s.get_confirmation()

        logging.info("The Zone Director is being upgraded. This process takes from 3 to 5 minutes. Please wait...")
        time_out = 1200
        start_time = time.time()
        while True:
            if time.time() - start_time > time_out:
                raise Exception("Error: Timeout")
            res = ping(zd.ip_addr)
            if res.find("Timeout") == -1:
                break
            time.sleep(2)
        logging.info("The Zone Director is being restarted. Please wait...")
        while True:
            if time.time() - start_time > time_out:
                raise Exception("Error: Timeout")
            res = ping(zd.ip_addr)
            if res.find("Timeout") != -1:
                break
            time.sleep(2)
        logging.info("The Zone Director has been upgraded successfully.")
        
        time.sleep(15)
        logging.info("Please wait while I am trying to navigate to the ZD's main URL[%s]." % zd.url)
        
        time_out = 900 
        start_time = time.time()
        while True:
            if time.time() - start_time > time_out:
                raise Exception("Error: Timeout. Cannot url to ZD[%s]." % zd.url)
            try:
                zd.s.open(zd.url)
                zd.current_tab = zd.LOGIN_PAGE
                time.sleep(2)
                if not zd.s.check_element_present(zd.info['loc_login_ok_button']):
                    continue
                logging.info('logging successfully')
                break
            except:
                time.sleep(5)
                pass
        


def verify_aps(zd, apList, timeout=900):
#    zd._login()
    timeS = time.time()
    for associated_ap in apList:
        while(True):
            if (time.time() - timeS) > timeout:
                raise Exception("Error: AP upgrading failed. Timeout")
            if (zd._get_ap_info(associated_ap['mac']))['status'] == associated_ap['status']:
                break


def verify_all_aps(zd, timeout=900):
    startT = time.time()
    while True :
        if time.time() - startT > timeout :
            raise Exception("AP connect failed. Timeout")
        infos = zd.get_all_ap_info()
        if len(infos) <= 0 :
            time.sleep(10)
            continue
        p = True
        for index in range(len(infos)) :
            if not infos[index]['status'].lower().startswith('connected') :
                p = False
                break
        if p :
            return True
            time.sleep(10)

def verify_aps_by_models(zd, models, timeout=1200):
    startT = time.time()
    while True :
        if time.time() - startT > timeout :
            raise Exception("AP connect failed. Timeout")
        infos = zd.get_all_ap_info()
        if len(infos) <= 0 :
            time.sleep(10)
            continue
        actualModels = []
        p = True
        for index in range(len(infos)) :
            if not infos[index]['status'].lower().startswith('connected') :
                p = False
                break
            if not actualModels.__contains__(infos[index]['model']) :
                actualModels.append(infos[index]['model'])
        for i in range(len(models)):
            if not actualModels.__contains__(models[i]):
                p = False
                break
        if p :
            return True
            time.sleep(20)
        
def retrieve_aps(zd):
    expectList = []
#    zd._login()
    l = zd.get_all_ap_info()
    for ap in l:
        if ap['status'].lower().startswith(u"connected"):
            expectList.append(ap)
            
    logging.info('APs number is [%s]' % len(expectList))
#    zd._logout()
    
    return expectList
    
def retrieve_aps_models(zd):
    apsInfo = zd.get_all_ap_info()
    models = []
    for index in range(len(apsInfo)):
        if not models.__contains__(apsInfo[index]['model']) :
            models.append(apsInfo[index]['model'])
            
    return models

def check_all_aps_status_from_cmd(zd_cli, ap_list, time_out=1200, chk_mac=False):
    """
        1.verify the number of all APs from console.
        2.loop checking all of APs are connected console.        
    """
    startTime = time.time()
    endTime = time.time()
    baseTime = time_out
    spanTime = 100
    
    expected_cnt = len(ap_list)
    invokeTime = baseTime + (expected_cnt / 50) * spanTime 
    
    logging.info('Begin checking all of APs status and make sure all of them are connected.')
    p = re.compile('.*Total.*:\s*(\d+)\s*')
    dynamic_cnt = 0
    while endTime - startTime < invokeTime :
        res = zd_cli.do_shell_cmd('show ap | grep Total', timeout=60)
        logging.info('APs Info:%s' % res)
        actual_cnt = 0
        result = p.match(res)
        if result:
            actual_cnt = int(result.group(1))           
        logging.info("There are [%d] APs have been managed, expect[%d]" % (actual_cnt, expected_cnt))
        if actual_cnt >= expected_cnt :
            if chk_mac :
                if check_aps_status_from_cli(zd_cli, ap_list, time_out=time_out) :
                    return True
                else:
                    break
            return True
        
        time.sleep(20)
        endTime = time.time()
        
        if endTime - startTime >= invokeTime and dynamic_cnt < actual_cnt :
                invokeTime = invokeTime + spanTime
                dynamic_cnt = actual_cnt
                
    logging.warning("Time out when wait for All APs connecting, leaped time[%d]" % time_out)
    return False

def check_aps_status_from_cli(zdcli, ap_list, time_out=1200):
    flag = True
    startTime = time.time()
    endTime = time.time()
    while endTime - startTime < time_out:
        for ap in ap_list:
            if not check_ap_status_from_cli(zdcli, ap['mac']):
                flag = False
                break
        if flag : return True
        time.sleep(50)   
        endTime = time.time()
    
def check_ap_status_from_cli(zdcli, mac_addr):
    res = zdcli.doCmd('show ap %s' % mac_addr, timeout=60)
    p = re.compile('^AP\s*([\da-fA-F:]{17}) not found$')
    if p.match(res):
        return False
    logging.info('AP[%s] has connected correctly' % mac_addr)
    return True
    
def check_aps_status_from_gui(zd, ap_list, time_out=1200, expr='^connected.*'):
    startTime = time.time()
    endTime = time.time()
    apcnt = len(ap_list)
    baseTime = time_out
    spanTime = 100
    dynamic_cnt = 0
    tmp_cnt = dynamic_cnt
    invokeTime = baseTime + (apcnt / 50) * spanTime     
    logging.info('begin to verify all of APs status.')
        
    while endTime - startTime < invokeTime :
        apInfos = AP.get_all_ap_info(zd)
        cur_cnt = len(apInfos)
        if cur_cnt < apcnt :
            time.sleep(20)
            endTime = time.time()
            if endTime - startTime >= invokeTime and dynamic_cnt > tmp_cnt:
                invokeTime = invokeTime + spanTime
                tmp_cnt = dynamic_cnt
                
        elif cur_cnt >= apcnt :
            allConnected = True
            for ap in ap_list :
                if not verify_ap(ap['mac'], apInfos, expr=expr) :
                    allConnected = False
                    break
                
            if allConnected :
                logging.info("all of expected have connected correctly.")
                return True
            
            time.sleep(20)
        else: time.sleep(20)
            
    return False
        
def verify_ap(apmac, apsInfo, expr='^connected.*'):
    p = re.compile(expr, re.I)
    for ap in apsInfo:
        if apsInfo[ap]['mac_address'] == apmac:
            if p.match(apsInfo[ap]['status']): 
                logging.info("ap[%s] has connected" % apmac)
                return True
            
            else:
                return False
            
    return False        


