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
        
        
Create on 2011-7-26
@author: cwang@ruckuswireless.com
'''

import logging
import trace

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector

from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Edit_Hotspot_Profiles(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(hotspot_profiles_list = [{'login_page': 'http://192.168.0.250/login.html', 
                                                   'name': 'A Sampe Hotspot Profile'},],                         
                        )
        self.conf.update(conf)
        self.hotspot_profiles_list = self.conf['hotspot_profiles_list']
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self._retrieve_carribag()
    
    def _retrieve_carribag(self):
        if not self.carrierbag.get('existing_authentication_sers'):
            self.carrierbag['existing_authentication_sers'] = lib.zd.aaa.get_auth_server_info_list(self.zd)
        for exit_auth_serv_info in self.carrierbag['existing_authentication_sers']:
            if self.conf.get('auth_svr') and exit_auth_serv_info['name'] == self.conf['auth_svr']:
                self.auth_svr = self.conf['auth_svr']                 
                self.conf.update({'authentication_server_type': exit_auth_serv_info['type']})
            elif self.conf.get('authentication_server') and exit_auth_serv_info['name'] == self.conf['authentication_server']:
                self.auth_svr = self.conf['authentication_server']
                self.conf.update({'authentication_server_type': exit_auth_serv_info['type']})
            else:
                pass
    
    def _update_carribag(self):
#         self.carrierbag['existed_hotspot_profile'] = lib.zd.wispr.get_all_profiles(self.zd)
        pass
     
    def config(self, conf):
        self._init_params(conf)
    
    def test(self):
        try:
            for hotspot in self.hotspot_profiles_list:                  
                #lib.zd.wispr.cfg_profile(self.zd, hotspot['name'], **hotspot)                
                lib.zdcli.hotspot.config_hotspot(self.zdcli, **hotspot)
        except:
            self.returnResult('FAIL', trace.sys.exc_traceback)
        
        return self.returnResult('PASS', 'hotspots %s update successfully' % self.hotspot_profiles_list)
    
    def cleanup(self):
        self._update_carribag()