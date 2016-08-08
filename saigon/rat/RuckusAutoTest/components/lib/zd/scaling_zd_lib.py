'''
Extract those common APIs which are relative with ZD. 
Created on 2010-2-9
@author: cwang@ruckuswireless.com
'''
import logging
import re
import time
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components.lib.zd import access_points_zd as AP
from RuckusAutoTest.common.sshclient import sshclient


def resolve_verify_all_aps(zd):
    list_of_connected_aps = list()
    
    apInfos = zd.get_all_ap_info()
    
    for ap in apInfos:
        if ap['status'].lower().startswith(u"connected"):
            list_of_connected_aps.append(ap)
    if len(list_of_connected_aps) == 0:
        raise Exception("No AP connected")      
    return list_of_connected_aps


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
    l = zd.get_all_ap_info()
    for ap in l:
        if ap['status'].lower().startswith(u"connected"):
            expectList.append(ap)
            
    logging.info('APs number is [%s]' % len(expectList))    
    return expectList
    
    
def retrieve_aps_models(zd):
    apsInfo = zd.get_all_ap_info()
    models = []
    for index in range(len(apsInfo)):
        if not models.__contains__(apsInfo[index]['model']) :
            models.append(apsInfo[index]['model'])
            
    return models


def check_aps_num_from_cmd(zd_cli, aps_num, time_out = 1200):
    '''
    Check how many aps are managed?
      expected_num:  <aps_num>
    '''
    startTime = time.time()
    endTime = time.time()
    baseTime = time_out
    spanTime = 100
    
    expected_cnt = aps_num
    invokeTime = baseTime + (expected_cnt / 50) * spanTime 
    
    logging.info('Begin checking all of APs status and make sure all of them are connected.')
    p = re.compile('.*Total.*:\s*(\d+)\s*')
    dynamic_cnt = 0
    while endTime - startTime < invokeTime :
        res = zd_cli.do_shell_cmd('wlaninfo -A  | grep Total', timeout=60)
        logging.info('APs Info:%s' % res)
        actual_cnt = 0
        result = p.match(res)
        if result:
            actual_cnt = int(result.group(1))           
        logging.info("There are [%d] APs have been managed, expect[%d]" % (actual_cnt, expected_cnt))
        if actual_cnt >= expected_cnt :
            return True,actual_cnt
        
        time.sleep(20)
        endTime = time.time()
        
        if endTime - startTime >= invokeTime and dynamic_cnt < actual_cnt :
                invokeTime = invokeTime + spanTime
                dynamic_cnt = actual_cnt
                
    logging.warning("Time out when wait for All APs connecting, leaped time[%d]" % time_out)
    return False,actual_cnt    

#get ap number in ZD from cli
#added by west.li
def get_aps_num_from_cmd(zd_cli,time_out=0):
    '''
    get number of aps are managed by zd
    '''
    logging.info('Begin checking all of APs status and make sure all of them are connected.')
    p = re.compile('.*Total.*:\s*(\d+)\s*')
    res = zd_cli.do_shell_cmd('wlaninfo -A  | grep Total', timeout=time_out)
    logging.info('APs Info:%s' % res)
    actual_cnt = 0
    result = p.match(res)
    if result:
        actual_cnt = int(result.group(1))           

    return actual_cnt    


def check_all_aps_status_from_cmd(zd_cli, aps_dict, time_out=1200, chk_mac=False):
    """
        1.verify the number of all APs from console.
        2.loop checking all of APs are connected console.        
    """
    startTime = time.time()
    endTime = time.time()
    baseTime = time_out
    spanTime = 100
    
    expected_cnt = len(aps_dict)
    invokeTime = baseTime + (expected_cnt / 50) * spanTime 
    
    logging.info('Begin checking all of APs status and make sure all of them are connected.')
    p = re.compile('.*Total.*:\s*(\d+)\s*')
    dynamic_cnt = 0
    while endTime - startTime < invokeTime :
        try:            
            res = zd_cli.do_shell_cmd('wlaninfo -A  | grep Total', timeout=60)
        except Exception, e:
            zdcli.zdcli = sshclient(self.zdcli.ip_addr, self.zdcli.port,'admin','admin')
            zd_cli.login()
            logging.debug(e.message)
            res = zd_cli.do_shell_cmd('wlaninfo -A | grep Total', timeout=60)
            
#        logging.info('APs Info:%s' % res)
        actual_cnt = 0
        result = p.match(res)
        if result:
            actual_cnt = int(result.group(1))           
        logging.info("There are [%d] APs have been managed, expect[%d]" % (actual_cnt, expected_cnt))
        if actual_cnt >= expected_cnt :
            if chk_mac :
                if check_aps_status_from_cli(zd_cli, aps_dict, time_out=time_out) :
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


def check_aps_status_from_cli(zdcli, aps_dict, time_out=1200):
    flag = True
    startTime = time.time()
    endTime = time.time()
    while endTime - startTime < time_out:
        for ap, ap_info in aps_dict.items():
            if not check_ap_status_from_cli(zdcli, ap_info['mac']):
                flag = False
                break            
        if flag : return True
        time.sleep(50)   
        endTime = time.time()

    
def check_ap_status_from_cli(zdcli, mac_addr):
    bugme.do_trace('test')
    res = zdcli.doCmd('show ap %s' % mac_addr, timeout=60)
    p = re.compile('^AP\s*([\da-fA-F:]{17}) not found$')
    if p.match(res):
        return False
    logging.info('AP[%s] has connected correctly' % mac_addr)
    return True


def get_ap_ip_addr_by_ap_mac(zdcli, mac_addr):
    res = zdcli.do_shell_cmd('show ap | grep %s' % mac_addr)
    p = re.compile('^((\d{1,3}\.){3}\d{1,3})\s*([\da-fA-F:]{17}).*')
    m_res = p.match(res)        
    if m_res and m_res.group(1):
        return m_res.group(1)
    

    
def check_aps_status_from_gui(zd, aps_dict, time_out=1200, expr='^connected.*'):
    startTime = time.time()
    endTime = time.time()
    apcnt = len(aps_dict)
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
                
        elif cur_cnt >= apcnt:
            allConnected = True
            for ap, ap_info in aps_dict:
                if not verify_ap(ap_info['mac'], apInfos, expr=expr) :
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

