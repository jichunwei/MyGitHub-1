'''
Description:
Created on 2010-11-4
@author: cwang@ruckuswireless.com
'''
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Set_SNMP_Trap_Info(Test):
    '''
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):        
        if self.conf.has_key('snmp_trap_cfg'):
            snmp_trap_cfg = self.conf['snmp_trap_cfg']
        else:
            snmp_trap_cfg = {'enabled': True,
                             'server_ip': u'192.168.0.252',
                             'version': 2}
        
        self.errmsg = lib.zd.sys.set_snmp_trap_info(self.zd, snmp_trap_cfg)
        self.snmp_trap_info = lib.zd.sys.get_snmp_trap_info(self.zd)
        self._update_carrier_bag()        
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:    
            return self.returnResult('PASS', 'Set SNMP Trap Info successfully')
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_snmp_trap_info'] = self.snmp_trap_info
    
    def _init_test_params(self, conf):
        self.conf = {}                        
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''
        self.passmsg = ''
    
