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
       To verify APs join to the AP group behavior list below:
            1. All new join AP will be assgined to the Default 
            AP group automatically.
            2. The APs can be selected to join the specify AP group.
            3. An AP can only be in one group at a time.
            4. Select APs table has filter function to help 
            administrators to choose APs more quickly.
            5. Move APs to other AP group works.          
   3. Cleanup:
       - 
    How it was tested:
        
        
Create on 2011-11-7
@author: cwang@ruckuswireless.com
'''

import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector

from RuckusAutoTest.components.lib.zd import ap_group
from RuckusAutoTest.components import Helpers

class CB_ZD_Join_AP_Group_Testing(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = {'ap_group_name':'AP_Group_1'}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.ap_group_name = self.conf['ap_group_name']
        
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        ap_group_found = ap_group.query_ap_group_brief_info_by_name(self.zd, 
                                                                    self.ap_group_name)
        if not ap_group_found:
            ap_group.create_ap_group(self.zd, self.ap_group_name)
            
        (res, message) = self._test_all_joining_aps_move_to_system_default_group()
        if res:
            return self.returnResult('PASS', message)
        
        return self.returnResult('FAIL', message)
    
    def cleanup(self):
        self._update_carribag()
    
    
    def _test_all_joining_aps_move_to_system_default_group(self):
        #All new join AP will be assgined to the Default AP group automatically.
        aps = self.zd.get_all_ap_info()
        all_aps_size = len(aps)        
        default_ap_group_cfg = ap_group.get_ap_group_cfg_by_name(self.zd, 'System Default')
        members_list = default_ap_group_cfg.pop('members_info')
        logging.info('members_list %s from System Default' % members_list)
        default_aps_size = len(members_list)
        if all_aps_size == default_aps_size:
            #move a ap to other AP Group.
            ap = aps[0]
            ap_mac = str(ap['mac'])            
            ap_group.move_ap_to_member_list(self.zd, self.ap_group_name, ap_mac)
            
        
        #Checking the AP numbers from different AP group
        ap_group_cfg = ap_group.get_ap_group_cfg_by_name(self.zd, self.ap_group_name)
        ap_group_members = ap_group_cfg['members_info']
        if len(ap_group_members)!=1:
            return (False, 'AP %s have not been move to AP Group %s' 
                    % (ap_mac, self.ap_group_name))
        
        logging.info('members %s in AP Group %s' % 
                     (ap_group_members, self.ap_group_name) )
        
        cur_default_ap_group_cfg = ap_group.get_ap_group_cfg_by_name(self.zd, 
                                                                     'System Default')
        
        logging.info('configuration %s in System Default AP Group' % cur_default_ap_group_cfg)
        
        if (len(cur_default_ap_group_cfg['members_info']) + 1) != default_aps_size:
            return (False, 'An AP can not be in two group at a time')
                
        
        #Remove all AP and wait for re-connect
        self.zd._delete_all_aps()
        logging.info('Wait for 100 seconds')
        time.sleep(100)

        #Updated by cwang@2012-7-18, Behavior change, after 9.5, AP will re-join to previous AP group other than System Default.
        res = ap_group.check_ap_assign_to_ap_group(self.zd, ap_mac, self.ap_group_name)
        if res:
            return (True, '[Correct Behavior]AP[%s] still keep in group[%s]' % (ap_mac, self.ap_group_name))

        else:
            return (False, '[Incorrect Behavior]AP[%s] lost in group[%s]' % (ap_mac, self.ap_group_name))

        #default_ap_group_cfg = ap_group.get_ap_group_cfg_by_name(self.zd, 'System Default')
        #members_list = default_ap_group_cfg.pop('members_info')
        #default_aps_size = len(members_list)
        #if all_aps_size == default_aps_size:            
        #    return (True, '[Correct behavior]All Joining APs should go to default group')
        
        #return(False, '[InCorrect behavior]Some Joining APs have not go to default group')
    
