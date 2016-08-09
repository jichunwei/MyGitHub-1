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
        
       
Create on Dec 2, 2011
@author: jluh@ruckuswireless.com
'''

import types
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_AP_Verify_Port_Base_Vlan_Setting(Test):
  required_components = ['ZoneDirector']
  parameters_description = {}
  
  
  def _init_params(self, conf):
       self.conf = {'ap_tag': '', 'expected_data_list': []}
       self.conf.update(conf)
       self.ap_tag = self.conf['ap_tag']
       self.expected_data_list = self.conf['expected_data_list']
       if type(self.expected_data_list) is types.ListType:
           for ex_data in self.expected_data_list:
               if ex_data['Mode'].lower() == 'lan1':
                  ex_data['Mode'] = 'eth0'
               elif ex_data['Mode'].lower() == 'lan2':
                   ex_data['Mode'] = 'eth1'
               elif ex_data['Mode'].lower() == 'lan3':
                   ex_data['Mode'] = 'eth2'
       else:
           if self.expected_data_list['Mode'].lower() == 'lan1':
                  self.expected_data_list['Mode'] = 'eth0'
           elif self.expected_data_list['Mode'].lower() == 'lan2':
                   self.expected_data_list['Mode'] = 'eth1'
           elif self.expected_data_list['Mode'].lower() == 'lan3':
                   self.expected_data_list['Mode'] = 'eth2'
       
       self.zd = self.testbed.components['ZoneDirector']
           
       self.passmsg = ''
       self.errmsg = ''
  
  
  def _retrieve_carribag(self, conf):
      try:
          self.active_ap = self.carrierbag[self.ap_tag]['ap_ins']
      except:
          self.active_ap = self.carrierbag['AP'][self.ap_tag]['ap_ins']
  
  
  def _update_carribag(self):
      pass
  
  
  def config(self, conf):
      self._init_params(conf)
      self._retrieve_carribag(conf)
  
  
  def test(self):
      self._verify_vlan_setting_on_ap_bridge()
      if self.errmsg:
          return self.returnResult('FAIL', self.errmsg)
      
      return self.returnResult('PASS', self.passmsg)
  
  
  def cleanup(self):
       pass


  def _verify_vlan_setting_on_ap_bridge(self):
      br_info = self.active_ap.get_bridge_setting('', 'br0')
      msg = ""
      for exp_data in self.expected_data_list: 
          for br in br_info:
              if br['Port'] == exp_data['Mode']:
                  if br['Untagged vlan'] == exp_data['Untagged vlan'] and \
                        br['Enabled vlans'] == exp_data['Enabled vlans']:
                      self.errmsg = ''
                      self.passmsg = 'The vlan setting is corrected on the ap side'
                      break 
                  else:
                      msg = "[expect] %s, %s, %s, [actual] %s, %s, %s\n" % (exp_data['Mode'], exp_data['Untagged vlan'], exp_data['Enabled vlans'], br['Port'], br['Untagged vlan'], br['Enabled vlans'])
              self.errmsg = "The vlan setting isn't corrected on the ap side\n"
              self.errmsg += msg