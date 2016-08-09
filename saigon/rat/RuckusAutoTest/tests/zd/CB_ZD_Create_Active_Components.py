'''
Created on Jan 24, 2014

@author: jacky luh

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

class CB_ZD_Create_Active_Components(Test):
    required_components = ['station', 'ap', 'linuxpc']
    parameters_description = {}
  
    def _init_params(self, conf):
        self.check_status_timeout=120
        self.conf = dict()
        self.conf.update(conf)
        self.passmsg = ''
        self.errmsg = ''
        
        self.carrierbag['zd'] = self.testbed.components['ZoneDirector']
        self.carrierbag['zdcli'] = self.testbed.components['ZoneDirectorCLI']
        
        for i_conf in self.conf:
            if i_conf in self.required_components:
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
        for u_component in self.required_components:
            if u_component == 'station':
                self._create_stations()
            
            if u_component == 'ap':
                self._create_active_aps()
                    
            if u_component == 'linuxpc':
                self._create_linux_pc()
                
                    
    def _create_stations(self):
        self.sta_ip_addr = self.conf['station']         
        self.target_station = tconfig.get_target_station(self.sta_ip_addr,
                                                         self.testbed.components['Station'],
                                                         check_status_timeout=self.check_status_timeout,
                                                         remove_all_wlan=True)
            
        self.carrierbag['station'] = self.target_station
        logging.info('Create station [%s] Successfully' % (self.sta_ip_addr))
            
        if not self.target_station:
            self.errmsg = "Target station [%s] not found" % (self.sta_ip_addr)
                
            
    def _create_active_aps(self):
        self.act_ap_tag = self.conf['ap']

        if self.testbed.ap_sym_dict.has_key(self.act_ap_tag):
            self.ap_macaddr = self.testbed.ap_sym_dict[self.act_ap_tag]['mac']
        else:
            raise Exception("Not found the active ap on the test bed's config")     
        self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.ap_macaddr)
        
        self.carrierbag['ap'] = self.active_ap
        logging.info('Create active ap [%s] successfully' % self.ap_macaddr)
        
        if not self.active_ap:
            self.errmsg = "Active ap [%s] not found in testbed." % self.ap_macaddr
            
            
    def _create_linux_pc(self):
        self.lpc_ip_addr = self.conf['linuxpc']
        
        if not self.testbed.config.get('server'):
            raise Exception("Not found the linux server component")
        
        if self.lpc_ip_addr == self.testbed.config['server']['ip_addr']:
            self.linux_pc = self.testbed.components['LinuxServer']
        else:
            raise Exception("Not found the linux server component")
            
        self.carrierbag['linuxpc'] = self.linux_pc
        logging.info('Create Linux PC [%s] Successfully' % (self.lpc_ip_addr))

        if not self.linux_pc:
            self.errmsg = "Linux PC [%s] not found" % (self.lpc_ip_addr)

                    
                
