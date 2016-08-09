'''
Description:
	Testing Access Point search functionality.

Created on 2010-6-9
@author: cwang@ruckuswireless.com
'''
import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import aps

class CB_ZD_Search_APs(Test):
    '''
    Test search function against monitor/access points
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        if not self.aps_list:
            self.aps_list = self.testbed.get_aps_sym_dict()
        
        self.aps_list = self.aps_list.values()
        mac_addr = self.aps_list[0]['mac']
        ap = self.zd.get_all_ap_info(mac_addr)
        
        
        self._test_search_by_mac(passmsg, mac_addr)
        self._test_search_by_ip(passmsg, ap)
        self._test_search_by_devname(passmsg, ap)
        
               
        self._update_carrier_bag()
        
        return self.returnResult('PASS', passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key('existing_aps_list'):
            self.aps_list = self.carrierbag['existing_aps_list']        
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(mac = [], ip = [], devname = [])
        self.conf.update(conf)
        
        self.mac_search_list = self.conf['mac']
        self.ip_search_list = self.conf['ip']
        self.devname_search_list = self.conf['devname']
        self.aps_list = None
        self.zd = self.testbed.components['ZoneDirector']
        
    
    def _test_search_by_mac(self, passmsg, mac_addr):
        if len(self.mac_search_list) == 0:
            mac = mac_addr
            self.mac_search_list.append(mac[:-2])                        
            self.mac_search_list.append(mac)
                    
        for mac in self.mac_search_list:
	    cnt = 3
	    while cnt:
	        try:
                    target_ap_list = aps.query_ap_details_by_sub_mac_addr(self.zd, mac)
		    break
	        except Exception, e:
		    logging.debug(e.message)
	            cnt = cnt - 1		    
		    if not cnt:
		        raise e
	            time.sleep(5)
	    
            if not self._verify_aps_by_type(target_ap_list, compare_type='mac'):
                return self.returnResult("FAIL", "when search ap by type 'mac', value=[%s] work incorrectly" % mac)
            
            msg = "when search ap by type 'mac', value=[%s] work correctly" % mac
            logging.info(msg)
            passmsg.append(msg)
            time.sleep(2)        
    
    def _test_search_by_ip(self, passmsg, ap):
        if len(self.ip_search_list) == 0:    
            ip_addr = ap['ip_addr']
            self.ip_search_list.append(ip_addr[:-2])
            self.ip_search_list.append(ip_addr)
                    
        for ip in self.ip_search_list:
	    cnt = 3
	    while cnt:
	        try:
                    target_ap_list = aps.query_ap_details_by_sub_ip_addr(self.zd, ip)
		    break
                except Exception, e:
		    logging.debug(e.message)
	            cnt = cnt - 1		    
		    if not cnt:
		        raise e
		    time.sleep(5)
            
            if not self._verify_aps_by_type(target_ap_list, compare_type='ip', value = ip):
                return self.returnResult("FAIL", "when search ap by type 'ip', value=[%s] work incorrectly" % ip)
            
            msg = "when search ap by type 'ip', value=[%s] work correctly" % ip
            
            logging.info(msg)
            passmsg.append(msg)
            time.sleep(2)   
            
    
    def _test_search_by_devname(self, passmsg, ap):
        if len(self.devname_search_list) == 0:
            dev_name = ap['device_name']
            self.devname_search_list.append(dev_name)
                    
        for devname in self.devname_search_list:
	    cnt = 3
	    while cnt:
	        try:
                    target_devname_list = aps.query_ap_details_by_dict(self.zd, key = 'devname', value = devname)
		    break
	        except Exception, e:
		    logging.debug(e.message)
	            cnt = cnt - 1		    
		    if not cnt:
		       raise e
		    time.sleep(5)
	            
            if not self._verify_aps_by_type(target_devname_list, compare_type='devname', value = devname):
                return self.returnResult('FAIL', "when search ap by type 'devname', value=[%s] work incorrectly" % devname)
            
            msg = "when search ap by type 'devname', value=[%s] work correctly" % devname 
            logging.info(msg)
            passmsg.append(msg)
            time.sleep(2)   
            
                             
    
    def _verify_aps_by_type(self, target_ap_list, compare_type='mac', value = ''):
        '''
            compare type including mac, ip etc.
        '''
        for tap in target_ap_list:
            tvalue = tap[compare_type]
            if tvalue.find(value) >=0:
                continue
            else:
                return False
        
        return True
