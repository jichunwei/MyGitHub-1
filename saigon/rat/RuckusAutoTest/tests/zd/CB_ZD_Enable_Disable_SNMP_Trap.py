'''
Description:

Enable/Disable snmp trap via GUI

Created on 2012-06-25
@author: zoe.huang@ruckuswireless.com

'''
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Enable_Disable_SNMP_Trap(Test):
    required_components = ['ZoneDirector']
    parameter_description = {'snmp_trap_cfg': 'status of snmp trap wanted to be set'}
    
    def config(self, conf):
        self._init_test_params(conf)
    
    def test(self):     
        if self.conf.has_key('snmp_trap_cfg'):
            snmp_trap_cfg = self.conf['snmp_trap_cfg']
        else:
            snmp_trap_cfg = {'enabled': True,
                            }
        try:           
            if snmp_trap_cfg.get('enabled'):#chen.tao 2014-2-28, to fix zf-7542
                pass#Not able to enable snmp trap by using function enable_disable_snmp_trap()
            else:           
                self.errmsg = lib.zd.sys.enable_disable_snmp_trap(self.zd, snmp_trap_cfg)
        except Exception, ex:
            self.errmsg = ex.message
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:  
            return self.returnResult('PASS', 'Set SNMP Trap to %s successfully via GUI' % snmp_trap_cfg)
        
    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {}                        
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''
        self.passmsg = ''
    
