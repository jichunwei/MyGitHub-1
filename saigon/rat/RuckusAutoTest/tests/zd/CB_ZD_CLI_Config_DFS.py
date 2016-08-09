'''
Description:
    Enable DFS from ZD CLI.
Create on 2013-8-8
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import system as LIB

class CB_ZD_CLI_Config_DFS(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(cc='US',
                         option='compatibility'
                         )
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.cc = self.conf.get('cc')
        self.option = self.conf.get('option')
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:            
            logging.info('Set countrycode %s channel optimization to %s' % \
                         (self.cc, self.option))
            LIB.set_channel_optimization(self.zdcli, self.cc, self.option)
            logging.info('Set Countrycode channel optimization-->DONE')
            
        except Exception, e:
            import traceback
            logging.error(traceback.format_exc())
            return self.returnResult('FAIL', e.message)
        
        return self.returnResult('PASS', 'Set DFS DONE.')
    
    def cleanup(self):
        self._update_carribag()
    
    