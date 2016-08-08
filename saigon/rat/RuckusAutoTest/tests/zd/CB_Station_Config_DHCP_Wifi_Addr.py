"""
   Description: 
   @author: Jane Guo
   @contact: guo.can@odc-ruckuswireless.com
   @since: May 2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:
        - 'ip_cfg': 'ip cfg'
        ip_cfg = {'source':'DHCP', 
        'addr' : '', 
        'mask' : '', 
        'gateway' : ''
        }
        - 'sta_tag': 'sta tag'
        - 'renew_ip' : True: update carrier bag
                       False: do nothing
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - set station ip config, if the ip_cfg is empty, use the cfg in carrie bag
          if use_diff_ip is true, modify the ip addr 
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Set station ip config success
            FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging
import re
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers

class CB_Station_Config_DHCP_Wifi_Addr(Test):
    required_components = ['Station']
    parameters_description = {'ip_cfg' : {},
                              'sta_tag' : 'sta_1',
                              'renew_ip' : True
                               }
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carrier_bag()
    
    def test(self): 
        logging.info('Config DHCP Wifi Addr')   
        try:
            self._set_dhcp_wifi_addr()
        except Exception, ex:
            self.errmsg = 'Config DHCP Wifi Addr:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:
            self._update_carrier_bag()
            pass_msg = 'Config DHCP Wifi Addr success'
            return self.returnResult('PASS', pass_msg)        
        
        
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf = {'ip_cfg' : {'source':'DHCP', 
        'addr' : '', 
        'mask' : '', 
        'gateway' : ''
        },
                    'sta_tag' : 'sta_1',
                    'renew_ip' : True
                               }
        self.conf.update(conf)
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']

        self.ip_cfg = self.conf['ip_cfg']
        self.renew_ip = self.conf['renew_ip']
        self.update_ip_cfg = {}           
        self.errmsg = ''     
    
    def _retrieve_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        if self.renew_ip:
            self.carrierbag[self.conf['sta_tag']]['wifi_ip_cfg'] = self.update_ip_cfg
            self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr'] = self.update_ip_cfg['addr']
 
    def _set_dhcp_wifi_addr(self):
        self.target_station.set_ip_if(self.ip_cfg['source'], self.ip_cfg['addr'], 
                                          self.ip_cfg['mask'], self.ip_cfg['gateway'])
        if self.renew_ip:
            self.target_station.renew_wifi_ip_address()
            #@author: Jane.Guo @since: 2013-06-18 after renew ip, need wait a little time to get new ip
            time.sleep(5)
            get_result = self.target_station.get_ip_config()
            
            if not get_result.get('ip_addr'):
                time.sleep(20)
                get_result = self.target_station.get_ip_config()
            
            logging.info("Get ip config: %s" % get_result)
            
            if get_result.get('ip_addr'):
                self.update_ip_cfg['source'] = 'DHCP'
                self.update_ip_cfg['addr'] = get_result.get('ip_addr')
                self.update_ip_cfg['mask'] = get_result.get('subnet_mask')
                self.update_ip_cfg['gateway'] = get_result.get('gateway')
            else:
                self.errmsg = "Get ip config from station fail"
