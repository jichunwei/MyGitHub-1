'''
Description:

Remove SNMP Trap info via CLI

Created on 2012-06-28
@author: zoe.huang@ruckuswireless.com

'''

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli.configure_snmp import remove_snmpv2_trap
from RuckusAutoTest.components.lib.zdcli.configure_snmp import remove_snmpv3_trap

class CB_ZD_CLI_Remove_SNMP_Trap(Test):
    
    required_components = ['ZoneDirectorCLI']
    parameter_description = {'snmpv2': 'format of SNMP trap',
                             'snmpv3': 'format of SNMP trap'}
    
    def config(self, conf):
        self._init_test_params(conf)
        
    def test(self):      
        self.errmsg = ''
        if self.conf.has_key('snmpv2'):
            result, res_dict = remove_snmpv2_trap(self.zdcli)
            if not result:
                self.errmsg = 'Delete snmpv2 trap info failed, Error: %s' % res_dict
                
        if self.conf.has_key('snmpv3'):
            result, res_dict = remove_snmpv3_trap(self.zdcli)
            if not result:
                self.errmsg = self.errmsg + ('Delete snmpv3 trap info failed, Error: %s' % res_dict)
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:  
            return self.returnResult('PASS', 'Delete snmp trap info via CLI successfully')
    
    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        self.errmsg = ''
        self.passmsg = ''  