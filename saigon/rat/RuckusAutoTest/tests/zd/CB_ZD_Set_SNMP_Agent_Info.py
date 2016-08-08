'''
Description:
Created on 2010-11-4
@author: cwang@ruckuswireless.com
'''
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Set_SNMP_Agent_Info(Test):
    '''
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
        
    def test(self):        
        self._set_snmpv2_cfg()
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:        
            self._update_carrier_bag()
            return self.returnResult('PASS', 'Set SNMP Agent V2 Info successfully')
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_snmp_agent_info'] = self.snmp_agent_cfg
    
    def _init_test_params(self, conf):
        default_agent_cfg = {'contact': u'support@ruckuswireless.com',
                             'enabled': True,
                             'location': u'880 West Maude Avenue, Suite 101, Sunnyvale, CA 94085 USA',
                             'ro_community': u'public',
                             'rw_community': u'private'}
        self.conf = {}
        self.conf.update({'snmp_agent_cfg': default_agent_cfg})
        self.conf.update(conf)        
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''
        self.passmsg = ''
        
    def _set_snmpv2_cfg(self):
        try:
            self.errmsg = lib.zd.sys.set_snmp_agent_info(self.zd,  self.conf['snmp_agent_cfg'])
            self.snmp_agent_cfg = lib.zd.sys.get_snmp_agent_info(self.zd)
        except Exception, ex:
            self.errmsg = ex.message 
