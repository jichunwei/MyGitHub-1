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

import types
import logging

import libZD_TestConfig as tconfig 
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import create_linux_station_by_ip_addr

#If you need add other components to this script, 
#please append the unit to required_components list,
#and update the method of create_test_components(self)
#-Jacky Luh
required_components = ['Station', 'AP', 'LinuxPC']
parameters_description = {}

class CB_ZD_Create_Test_Components(Test):
  
    def _init_params(self, conf):
        self.check_status_timeout=120
        self.conf = dict()
        self.conf.update(conf)
        self.passmsg = ''
        self.errmsg = ''
        self.zd = self.testbed.components['ZoneDirector']
      
        for i_conf in self.conf:
            if i_conf in required_components:
                if not self.carrierbag.has_key(i_conf):
                    self.carrierbag[i_conf] = {}
                if type(self.conf[i_conf]) is types.ListType:
                    for u_conf in self.conf[i_conf]:
                        for lv in u_conf:
                            if 'tag' in lv:
                                if not self.carrierbag[i_conf].has_key(u_conf[lv]):                                   
                                    self.carrierbag[i_conf][u_conf[lv]] = {}
                else:
                    for u_conf in self.conf[i_conf]:
                        if 'tag' in u_conf and (not self.carrierbag[i_conf]):
                            self.carrierbag[i_conf][self.conf[i_conf][u_conf]] = {}
            else:
                logging.info('please enhance the script to surpport the component[%s].' %i_conf)
  
  
    def _retrieve_carribag(self, conf):
        pass
  
  
    def _update_carribag(self):
        pass
      
       
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag(conf)
  
  
    def test(self):
        self.create_test_components()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
      
        passmsg = 'Config test env components successfully'
        return self.returnResult('PASS', passmsg)
  
    def cleanup(self):
        pass
      
     
    def create_test_components(self):
        for u_component in required_components:
            if u_component == 'Station':
                self._create_stations(self.conf[u_component])
          
            if u_component == 'AP':
                self._create_active_aps(self.conf[u_component])
                  
            if u_component == 'LinuxPC':
                self._create_linux_pcs(self.conf[u_component])
              
                  
    def _create_stations(self, conf):
        self.sta_config_list = []
        if type(conf) is types.ListType:
            self.sta_config_list = conf
        else:
            self.sta_config_list = [conf,]
                      
        for sta in self.sta_config_list:
            self.sta_tag = sta['sta_tag']
            self.sta_ip_addr = sta['sta_ip_addr']
          
            if not (self.carrierbag['Station'].has_key(self.sta_tag) and \
                self.carrierbag['Station'][self.sta_tag]):          
                self.target_station = tconfig.get_target_station(self.sta_ip_addr
                                                     , self.testbed.components['Station']
                                                     , check_status_timeout=self.check_status_timeout
                                                     , remove_all_wlan=True)
              
                self.carrierbag[required_components[0]][self.sta_tag]['sta_ins'] = self.target_station
                logging.info('Create Station [%s %s] Successfully' % (self.sta_tag, self.sta_ip_addr))
              
                if not self.target_station:
                    self.errmsg = "Target station [%s %s] not found" % (self.sta_tag, self.sta_ip_addr)
              
          
    def _create_active_aps(self, conf):
        self.ap_config_list = []
        if type(conf) is types.ListType:
            self.ap_config_list = conf
        else:
            self.ap_config_list = [conf,]
          
        for a_ap in self.ap_config_list:
            self.act_ap_tag = a_ap['ap_tag']
            self.active_ap_symbolic_name = a_ap['active_ap']
          
            if not (self.carrierbag['AP'].has_key(self.act_ap_tag) and \
                     self.carrierbag['AP'][self.act_ap_tag]):             
                self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.active_ap_symbolic_name)
                  
                self.carrierbag['AP'][self.act_ap_tag]['ap_ins'] = self.active_ap
                logging.info('Create active AP [%s %s] successfully' % (self.active_ap.get_ap_model(), self.active_ap.get_base_mac()))
                  
                if not self.active_ap:
                    self.errmsg = "Active AP [%s] not found in testbed." % self.active_ap_symbolic_name
          
          
    def _create_linux_pcs(self, conf):
        self.lpc_config_list = []
        if type(conf) is types.ListType:
            self.lpc_config_list = conf
        else:
            self.lpc_config_list = [conf,]

        for l_pc in self.lpc_config_list:
            self.lpc_tag = l_pc['lpc_tag']
            self.lpc_ip_addr = l_pc['lpc_ip_addr']
          
            if not (self.carrierbag['LinuxPC'].has_key(self.lpc_tag) and \
                 self.carrierbag['LinuxPC'][self.lpc_tag]):         
                self.linux_pc = self.testbed.components[self.lpc_tag]
              
                self.carrierbag['LinuxPC'][self.lpc_tag]['lpc_ins'] = self.linux_pc
                logging.info('Create Linux PC [%s %s] Successfully' % (self.lpc_tag, self.lpc_ip_addr))

                if not self.linux_pc:
                    self.errmsg = "Linux PC [%s %s] not found" % (self.lpc_tag, self.lpc_ip_addr)
