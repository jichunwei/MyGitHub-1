'''
Description:  
Create on 2014-1-24
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_aaa_servers as cfgHlp

class CB_ZD_CLI_Test_Negative_AAA(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(server_cfg_list=[])
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.server_cfg_list = self.conf.get('server_cfg_list')
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        logging.info('Configure AAA Servers in ZD CLI')
        try:
            cfgHlp.delete_all_servers(self.zdcli)            
            res, msg = cfgHlp.configure_aaa_servers(self.zdcli, self.server_cfg_list)
            logging.error(msg)
            return self.returnResult('FAIL', "Can set attribute grp-search")            
        except Exception, ex:            
            import traceback
            logging.info('Correct Behavior:')
            logging.info(traceback.format_exc())
            return self.returnResult('PASS', "Can't set attribute grp-search.")
    
    def cleanup(self):
        self._update_carribag()
        