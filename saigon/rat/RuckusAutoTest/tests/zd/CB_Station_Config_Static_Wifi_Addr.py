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
        ip_cfg = {'source':'Static', 
        'addr' : '192.168.0.231', 192.168.10.110
        'mask' : '255.255.0.0', 
        'gateway' : '192.168.0.253'
        }
        - 'sta_tag': 'sta tag'
        - use_diff_ip: True: we use ip config from carriebag and modify ip addr
                       False:we use ip config from carriebag
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

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers

class CB_Station_Config_Static_Wifi_Addr(Test):
    required_components = ['Station']
    parameters_description = {'ip_cfg' : {},
                              'sta_tag' : 'sta_1',
                              'use_diff_ip' : False,
                              'renew_ip' : True
                               }
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carrier_bag()
    
    def test(self): 
        logging.info('Config Static Wifi Addr')     
        try:
            self._set_static_wifi_addr()
        except Exception, ex:
            self.errmsg = 'Config Static Wifi Addr:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:
            self._update_carrier_bag()
            pass_msg = 'Config Static Wifi Addr success'
            return self.returnResult('PASS', pass_msg)        
        
        
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf = {'ip_cfg' : {'source':'Static', 
        'addr' : '192.168.0.231', 
        'mask' : '255.255.0.0', 
        'gateway' : '192.168.0.253'
        },
                    'sta_tag' : 'sta_1',
                    'use_diff_ip' : False,
                    'renew_ip' : True
                               }
        self.conf.update(conf)
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
           
        self.ip_cfg = self.conf['ip_cfg']
        self.use_diff_ip = self.conf['use_diff_ip'] 
        self.renew_ip = self.conf['renew_ip']
        self.update_ip_cfg = {}           
        self.errmsg = ''     
    
    def _retrieve_carrier_bag(self):
        if self.carrierbag[self.conf['sta_tag']].has_key('wifi_ip_cfg'):
            self.wifi_ip_cfg = self.carrierbag[self.conf['sta_tag']]['wifi_ip_cfg']
    
    def _update_carrier_bag(self):
        if self.renew_ip:
            self.carrierbag[self.conf['sta_tag']]['wifi_ip_cfg'] = self.update_ip_cfg
 
    def _set_static_wifi_addr(self):
        if self.ip_cfg:
            self.target_station.set_ip_if(self.ip_cfg['source'], self.ip_cfg['addr'], 
                                          self.ip_cfg['mask'], self.ip_cfg['gateway'])
            self.update_ip_cfg = self.ip_cfg            
        else:
            self.update_ip_cfg = self.wifi_ip_cfg 
            if self.use_diff_ip:
                #modify ip of carrier bag
                if not self.wifi_ip_cfg:
                    self.errmsg = "Can't find wifi_ip_cfg in carrie bag"
                    return
                match_ip = re.match('(\d*.\d*.\d*.)(\d*)', self.wifi_ip_cfg['addr'])  
                host_ip = int(match_ip.group(2)) + 20  
                new_ip = str(match_ip.group(1)) + str(host_ip)
                self.target_station.set_ip_if('Static', new_ip, 
                                              self.wifi_ip_cfg['mask'], self.wifi_ip_cfg['gateway'])
                self.update_ip_cfg['addr'] = new_ip
                           
            else:
                #use carriber bag info
                self.target_station.set_ip_if('Static', self.wifi_ip_cfg['addr'], 
                                              self.wifi_ip_cfg['mask'], self.wifi_ip_cfg['gateway'])

