"""
this case used to create an aaa server or edit an exist aaa server
by West.li
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import aaa_servers as aaa_cli

class CB_ZDCLI_Config_AAA_Server(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        aaa_cli.cfg_aaa_server(self.zdcli, self.conf)
        return self.returnResult('PASS', "aaa server configure successfully")
        
    def cleanup(self):
        pass

    def _cfgInitTestParams(self, conf):
        '''
        conf:
        {
            'name':'',#old name(option)
            'server_name':'',#new name
            'server_type':'',#ad/ldap/radius-auth/tacplus-auth
            'server_addr':'',
            'server_port':'',
            'tacacs_auth_secret':'',
            'tacacs_service':''
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
    