'''
Description:
    
Create on 2013-8-14
@author: cwang@ruckuswireless.com
'''

import logging
from copy import deepcopy

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector

from RuckusAutoTest.components.lib.zdcli import configure_ap as LIB

class CB_ZD_CLI_Config_APs_IPmode(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = {'mac_addr': None,          
                     'network_setting': {'ip_version': 'ipv4',},    
          }
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
        apmaclist = self.testbed.get_aps_sym_dict_as_mac_addr_list()
        cfg = self.conf
        self.apcfglist = []
        for ap in apmaclist:
            tcfg = deepcopy(cfg)   
            tcfg['mac_addr'] = ap             
            self.apcfglist.append(tcfg)
        
    
    def test(self):                
        try:
            logging.info('Prepare for changing IP Mode.')
            LIB.configure_aps(self.zdcli, self.apcfglist)
        except Exception, e:
            import traceback
            logging.error(traceback.format_exc())
            return self.returnResult('FAIL', e.message)
        
        return self.returnResult('PASS', 'Update AP IP Mode DONE.')
    
    def cleanup(self):
        self._update_carribag()
        