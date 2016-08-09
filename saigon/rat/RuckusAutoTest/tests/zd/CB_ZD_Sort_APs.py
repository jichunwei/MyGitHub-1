'''
Description:
	Test Access point sort functionality.
Created on 2010-6-9
@author: cwang@ruckuswireless.com
'''
import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import aps

class CB_ZD_Sort_APs(Test):
    '''
    Test sort APs functionality.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        
        if not self.aps_list:
            self.aps_list = self.testbed.get_aps_sym_dict()
            
        self.aps_list = self.aps_list.values()
        if len(self.mac_search_list) == 0:
            mac = self.aps_list[0]['mac']
	    #Ignore short search option, this will take lots of time.
            #self.mac_search_list.append(mac[0:3])
            #self.mac_search_list.append(mac[0:5])
	    self.mac_search_list.append(mac[:-3])
	    self.mac_search_list.append(mac[:-2])
	    self.mac_search_list.append(mac[:-1])
                                
        for mac in self.mac_search_list:
            if mac:
                #test asc
		cnt = 3
		while cnt:
		    try:
                        target_ap_list = aps.sort_ap_details_by_mac_addr_with_mac_filter(self.zd, mac, sort_type='asc')
			break
	            except Exception, e:
			logging.debug(e.message)
		        cnt = cnt - 1			
		        if not cnt:
			    raise e
			time.sleep(5)

                if not self._verify_aps_by_type(target_ap_list, compare_type = 'mac', value = mac):
                    return self.returnResult("FAIL", 'sort by mac[%s] as asc incorrectly' % mac)
                
                self._verify_sorted_list_by_type(target_ap_list, sort_type = 'asc', compare_type = 'mac')
                msg = 'sort by mac[%s] as asc correctly' % mac
                logging.info(msg)
                passmsg.append(msg)
                
                #test desc

		cnt = 3
		while cnt:
		    try:
                        target_ap_list = aps.sort_ap_details_by_mac_addr_with_mac_filter(self.zd, mac, sort_type='desc')
			break
	            except Exception, e:
			logging.debug(e.message)
		        cnt = cnt - 1			
		        if not cnt:
			    raise e
			time.sleep(5)

                if not self._verify_aps_by_type(target_ap_list, compare_type = 'mac', value = mac):
                    return self.returnResult("FAIL", 'sort by mac[%s] as desc incorrectly' % mac)
                
                self._verify_sorted_list_by_type(target_ap_list, sort_type = 'desc', compare_type = 'mac')
                msg = 'sort by mac[%s] as desc correctly' % mac
                logging.info(msg)
                passmsg.append(msg)
                                                                                
                
        self._update_carrier_bag()
        
        return self.returnResult("PASS", passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key('existing_aps_list'):
            self.aps_list = self.carrierbag['existing_aps_list']
        else:
            self.aps_list = []               
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(mac = [])
        self.conf.update(conf)
        self.mac_search_list = self.conf['mac']
        self.zd = self.testbed.components['ZoneDirector']
    
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
    
    def _verify_sorted_list_by_type(self, target_ap_list, sort_type='asc', compare_type = 'mac'):
        '''
        '''
        if len(target_ap_list)==0:
            return
        
        first = second = target_ap_list[0][compare_type]
        for index in range(1, len(target_ap_list)):
            second = target_ap_list[index][compare_type]
            if sort_type == 'asc' and first > second:
                raise Exception('correct value should be ap[%s] < ap[%s]' % (first, second))
            
            elif sort_type == 'desc' and first < second:
                raise Exception('correct value should be ap[%s] > ap[%s]' % (first, second))
            
            first = second
        
        return True
        
