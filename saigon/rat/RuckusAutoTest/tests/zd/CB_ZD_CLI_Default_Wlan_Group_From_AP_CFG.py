'''
Description:
Set All AP configuration WLAN Group to Default        
Create on 2013-5-28
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector

from RuckusAutoTest.components import Helpers

class CB_ZD_CLI_Default_Wlan_Group_From_AP_CFG(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        logging.info('Remove all WLAN groups from ZD CLI')
        try:
            ap_mac_list = self.testbed.get_aps_mac_list()
            logging.info("Default WLAN Groups for All APs")
            Helpers.zdcli.aps.default_wlan_groups_by_mac_addr(self.zdcli, ap_mac_list)                            
        except Exception, ex:
            logging.debug(traceback.format_exc())            
            return self.returnResult('FAIL', ex.message)
           
        return self.returnResult('PASS', 'Default WLAN Group from AP CFG DONE.')
    
    def cleanup(self):
        self._update_carribag()