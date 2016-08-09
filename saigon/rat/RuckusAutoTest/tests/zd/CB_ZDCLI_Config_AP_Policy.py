"""
config ap policy:
by West.li
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import config_ap_policy as ap_policy_cli

class CB_ZDCLI_Config_AP_Policy(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        ap_policy_cli.set_ap_polic(self.zdcli, self.conf)
        if self.conf.get('limited_zd_discovery'):
            ap_policy_cli.cfg_limited_zd_discovery(self.zdcli, self.conf['limited_zd_discovery'])
        return self.returnResult('PASS', "set ap policy via zdcli successfully")
        
    def cleanup(self):
        pass

    def _cfgInitTestParams(self, conf):
        '''
        conf:
        {
            'auto_approve':True/False,
            'mgmt_vlan':1/2/3/.../302/.../Keeping,
            'limited_zd_discovery':{
                                      'enabled':True/False,
                                      'primary_zd_ip':'192.168.0.2',
                                      'secondary_zd_ip':'192.168.0.3',
                                      'keep_ap_setting':True/False,
                                      'prefer_prim_zd':True/False,
                                    }
            'zdcli':'zdcli1'/'zdcli1'/...(in carrierbag)
            
        }
        '''
        self.errmsg = ''
        self.conf={
                   }
        self.conf.update(conf)
        if self.conf.has_key('mgmt_vlan') and self.conf['mgmt_vlan']:
            self.conf['vlan_id'] = self.conf['mgmt_vlan']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        if self.conf.get('zdcli'):
            self.zdcli = self.carrierbag[self.conf['zdcli']]
        
    def _update_carrierbag(self):
        pass
    