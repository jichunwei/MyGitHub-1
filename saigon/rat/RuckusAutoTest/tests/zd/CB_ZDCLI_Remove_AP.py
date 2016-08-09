"""
this case used to create an aaa server or edit an exist aaa server
by West.li
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli.configure_ap import del_aps_by_mac

class CB_ZDCLI_Remove_AP(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        del_aps_by_mac(self.zdcli,self.ap_mac_list)
        return self.returnResult('PASS', "aps removed successfully")
        
    def cleanup(self):
        pass

    def _cfgInitTestParams(self, conf):
        
        self.errmsg = ''
        self.conf={'ap_mac_list':[],
                   'zdcli':''
                   }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        if self.conf.get('zdcli'):
            self.zdcli = self.carrierbag[self.conf['zdcli']]
        self.ap_mac_list = self.conf['ap_mac_list']
        
    def _update_carrierbag(self):
        pass
    