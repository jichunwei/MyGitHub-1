'''
Description:
    Update AP management VLAN via ZDCLI interface.
        vlan_id: keeping|<vlan-number>
        return PASS, if update mgmt VLAN success.
        return FAIL, if update mgmt VLAN FAIL.
    
    Notes:
        Need get mgmt vlan before | after and compare expected value.
Create on 2013-8-9
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import config_ap_policy as LIB

class CB_ZD_CLI_Enable_AP_MgmtVlan(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(vlan_id = 'keeping')
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.ap_mgmt_vlan = self.conf.get('vlan_id')
        self.error_msg = ''
        self.pass_msg = ''
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        _policy_cfg = LIB.get_ap_policy(self.zdcli)
        _vlan_cfg = _policy_cfg.get('Management VLAN')
        _vlan_id = _vlan_cfg.get('VLAN ID')
        logging.info('Get current AP management VLAN status %s' % _vlan_id)
        logging.info('Try to update AP management VLAN %s' % self.ap_mgmt_vlan)
        LIB.set_ap_polic(self.zdcli, self.conf)
        logging.info('Update AP management VLAN DONE')
        _policy_cfg_next = LIB.get_ap_policy(self.zdcli)
        _vlan_cfg_next = _policy_cfg_next.get('Management VLAN')
        _vlan_id_next = _vlan_cfg_next.get('VLAN ID')
        logging.info('Current AP Management VLAN is %s' % _vlan_id)
        
        if self.ap_mgmt_vlan == "keeping":
            if _vlan_id_next == "Keep AP's setting":
                self.pass_msg = "AP Management VLAN is 'Keep AP's setting'"
            else:
                self.error_msg = "AP Management VLAN is wrong as '%s'" % _vlan_id_next
        else:
            if self.ap_mgmt_vlan != _vlan_id_next:
                self.error_msg = "AP Management VLAN is wrong as '%s'" % _vlan_id_next
            else:
                self.pass_msg = 'Set AP Management VLAN successfully'        
        
        if self.error_msg:                
            return self.returnResult('FAIL', self.error_msg)
        else:
            return self.returnResult('PASS', self.pass_msg)
    
    def cleanup(self):
        self._update_carribag()