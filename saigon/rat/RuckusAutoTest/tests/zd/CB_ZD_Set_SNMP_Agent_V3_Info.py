'''
Author: Cherry Cheng
Email: cherry.cheng@ruckuswireless.com
Description:
    This script is to set snmp agent v3 information from GUI.
'''

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Set_SNMP_Agent_V3_Info(Test):
    '''
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
        
    def test(self):
        self._set_snmpv3_cfg()
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()        
            return self.returnResult('PASS', 'Set SNMP Agent V3 Info successfully')        
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_snmp_agent_v3_info'] = self.snmp_agent_v3_cfg
    
    def _init_test_params(self, conf):
        default_snmpv3_cfg = {'enabled': False,
                              'ro_sec_name': 'ruckus-read',
                              'ro_auth_protocol': 'MD5',
                              'ro_auth_passphrase': '12345678',
                              'ro_priv_protocol': 'None',
                              'ro_priv_passphrase': '12345678',
                              'rw_sec_name': 'ruckus-write',
                              'rw_auth_protocol': 'MD5',
                              'rw_auth_passphrase': '12345678',
                              'rw_priv_protocol': 'None',
                              'rw_priv_passphrase': '12345678',}
        self.conf = {}
        if conf.has_key('snmp_agent_cfg'):
            default_snmpv3_cfg.update(conf['snmp_agent_cfg'])
            
        self.conf['snmp_agent_cfg'] = default_snmpv3_cfg
         
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''
        self.passmsg = ''
        
    def _set_snmpv3_cfg(self):
        try:
            self.errmsg = lib.zd.sys.set_snmp_agent_v3_info(self.zd, self.conf['snmp_agent_cfg'])
            self.snmp_agent_v3_cfg = lib.zd.sys.get_snmp_agent_v3_info(self.zd)
                                                
        except Exception, ex:
            self.errmsg = ex.message