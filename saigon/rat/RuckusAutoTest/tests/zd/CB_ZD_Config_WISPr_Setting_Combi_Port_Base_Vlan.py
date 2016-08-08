'''
Description:

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector', 'RuckusAP'
   Test parameters: 
   Result type: PASS/FAIL
   Results: PASS:
            FAIL:  

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - 
   2. Test:
       -            
   3. Cleanup:
       - 
    How it was tested:
        
       
Create on Nov 28, 2011
@author: jluh@ruckuswireless.com
'''

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8

class CB_ZD_Config_WISPr_Setting_Combi_Port_Base_Vlan(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
  
  
    def _init_params(self, conf):
        self.conf = dict(check_wlan_timeout = 60)
        self.conf.update(conf)
       
        self.zd = self.testbed.components['ZoneDirector']
       
        self.ap_tag = self.conf['ap_tag']
        self.wlan_cfg = self.conf['wlan_cfg']
        self.wgs_cfg = self.conf['wgs_cfg']
        self.username = self.conf['username']
        self.password = self.conf['password']
        self.wlan_name_list = [self.wlan_cfg['ssid']]
        self._retrieve_carribag()
        self.passmsg = ''
        self.errmsg = ''
  
  
    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag['AP'][self.ap_tag]['ap_ins']
  
    def _update_carribag(self):
        pass
  
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
  
    def test(self):    
        self._create_local_user()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        self._create_hotspot_profiles()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        self._create_hotspot_wlan_wg_assign_ap()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)

        self.passmsg = "Config a WISPr. Setting successfully on ZD" 
        return self.returnResult("PASS", self.passmsg)
  
    def cleanup(self):
        pass
         
    def _create_local_user(self):
        logging.info("Create a local user on the ZD")
        self.zd.create_user(self.username, self.password)
      
    def _create_hotspot_profiles(self):
        if self.conf['hotspot_profiles_list']:
            try:
                for profile in self.conf['hotspot_profiles_list']:
                    lib.zd.wispr.create_profile(self.zd, **profile)
                    time.sleep(1)
            except Exception, e:
                self.errmsg = '%s' % e.message
        else:
            raise Exception('No hotspot profile cfg on test config.') 
        logging.info('The Hotspot profile[%s] was created successfully' % self.conf['hotspot_profiles_list'])
      
#      self.carrierbag['existed_hotspot_profile'] = lib.zd.wispr.get_all_profiles(self.zd)
      
    def _create_hotspot_wlan_wg_assign_ap(self):
        self._cfg_create_wlan_on_zd()
        if self.errmsg:
            return ''
        self._rm_wlan_from_default_wlangroup()
        if self.errmsg:
            return ''
        self._cfg_create_empty_wlan_group_on_zd()
        if self.errmsg:
            return ''
        self._cfg_assign_wlan_to_wlangroup()
        if self.errmsg:
            return ''
        self._assign_wlan_group_on_ap()
        if self.errmsg:
            return ''
      
    def _cfg_create_wlan_on_zd(self):
        logging.info("Create WLAN [%s] as a hotspot WLAN on the Zone Director" % self.wlan_cfg['ssid'])
        lib.zd.wlan.create_wlan(self.zd, self.wlan_cfg)
        self.errmsg = tmethod8.pause_test_for(self.conf['check_wlan_timeout'], "Wait for the ZD to push new configuration to the APs")

    def _rm_wlan_from_default_wlangroup(self):
        self.errmsg = lib.zd.wgs.uncheck_default_wlan_member(self.zd, self.wlan_cfg['ssid'])

    def _cfg_create_empty_wlan_group_on_zd(self):
        self.errmsg = lib.zd.wgs.create_wlan_group(self.zd, self.wgs_cfg['name'], [], False, self.wgs_cfg['description'])
    
    def _cfg_assign_wlan_to_wlangroup(self):   
        self.errmsg = lib.zd.wgs.cfg_wlan_group_members(self.zd, self.wgs_cfg['name'], self.wlan_name_list, True)        
        
    def _assign_wlan_group_on_ap(self):
        self.errmsg = lib.zd.ap.cfg_wlan_groups_by_mac_addr(self.zd, [self.active_ap.get_base_mac()], self.wgs_cfg['ap_rp'], self.wgs_cfg['description'])     
