"""
this case used to remove an exist aaa server
by West.li
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import aaa_servers as aaa_cli

class CB_ZDCLI_Remove_AAA_Server(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        aaa_cli.remove_aaa_server(self.zdcli, self.conf['name'])
        return self.returnResult('PASS', "aaa server configure successfully")
        
    def cleanup(self):
        pass

    def _cfgInitTestParams(self, conf):
        '''
        conf:
        {
            'name':'',
        }
        '''
        self.errmsg = ''
        self.conf={
                   }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
    def _update_carrierbag(self):
        pass
    