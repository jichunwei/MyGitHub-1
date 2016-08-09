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
        
        
Create on 2011-11-10
@author: cwang@ruckuswireless.com
'''

import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector

from RuckusAutoTest.components.lib.zd import ap_group

class CB_ZD_Move_AP_Group_Testing(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = {'ap_group_name':'AP_Group_1',
                     'move_to_group_name':'AP_Group_Move',
                     }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.ap_group_name = self.conf['ap_group_name']
        self.move_to_group_name = self.conf['move_to_group_name']
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        
        ap_list = self.zd.get_all_ap_info()
        default_ap_list = ap_group.get_ap_group_cfg_by_name(self.zd, 'System Default')
        if(len(ap_list) != len(default_ap_list['members_info'])):
           ap_group.delete_all_ap_group(self.zd)
                                
        
        ap_group_found = ap_group.query_ap_group_brief_info_by_name(self.zd, 
                                                                    self.ap_group_name)
        if not ap_group_found:
            ap_group.create_ap_group(self.zd, self.ap_group_name)
        
        move_ap_group_found = ap_group.query_ap_group_brief_info_by_name(self.zd, 
                                                                    self.move_to_group_name)
        if not move_ap_group_found:
            ap_group.create_ap_group(self.zd, self.move_to_group_name)
        
        logging.info('Try to move all AP to %s AP Group' % self.ap_group_name)
        existed_ap_mac_list = [str(ap['mac']) for ap in ap_list]        
        ap_group.move_ap_to_member_list(self.zd, 
                                        self.ap_group_name, 
                                        existed_ap_mac_list)
        
        ap_mac = existed_ap_mac_list[0]
        logging.info('Try to move AP %s to %s AP Group' % (ap_mac, 
                                                          self.ap_group_name))
        ap_group.move_aps_to_ap_group(self.zd, ap_mac, 
                                      self.ap_group_name, 
                                      self.move_to_group_name)
        
        source_ap_group = ap_group.get_ap_group_cfg_by_name(self.zd, 
                                                            self.ap_group_name)
        target_ap_group = ap_group.get_ap_group_cfg_by_name(self.zd, 
                                                            self.move_to_group_name)
        if len(source_ap_group['members_info'])!= (len(existed_ap_mac_list) -1):
            return self.returnResult('FAIL', 'AP %s is still in the AP Group %s' % 
                                     (ap_mac, self.ap_group_name))
        
        if len(target_ap_group['members_info'])!=1:
            return self.returnResult('FAIL', 
                                     'AP Group %s should contain one AP, actual is %d' % 
                                     (self.move_to_group_name, 
                                      len(target_ap_group['members_info'])))
        
        if target_ap_group['members_info'][0]['mac']!=ap_mac:
            return self.returnResult('FAIL', 'AP %s has not been moved to AP Group %s' % 
                                     (ap_mac, self.move_to_group_name))
        
        #Checking the System Default Info:
        default_group = ap_group.get_ap_group_cfg_by_name(self.zd, 'System Default')
        size = len(default_group['members_info'])
        if size != 0:
            return self.returnResult('FAIL', 
                                     'System Group contains %d APs,\
                                      expected Zero' % size)
        
        default_mac_list = [item['mac'] for item in default_group['members_info']]
        
        if ap_mac in default_mac_list:
            return self.returnResult('FAIL', 'AP %s is still in System Default' %
                                      ap_mac)
            
        return self.returnResult('PASS', 'Move APs to other AP group works')
    
    def cleanup(self):
        self._update_carribag()