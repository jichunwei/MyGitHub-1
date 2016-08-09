'''
Author: Cherry Cheng
Email: cherry.cheng@ruckuswireless.com
Description:
    This script is to verify whether snmpd process is started.
'''
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import sys_snmp_info as lib

class CB_ZD_CLI_Verify_SNMPD_Process(Test):
    '''
    '''
    required_components = ['ZoneDirectorCLI']
    parameter_description = {'enabled': 'if true, verify snmpd process in ps list, if false, verify snmpd is not in ps list'}
    
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):                
        self._verify_snmpd_process()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)    
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):        
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _verify_snmpd_process(self):
        try:
            is_enabled = self.conf['enabled']            
            result = lib.check_snmpd_process(self.zdcli)
            
            if is_enabled != result:
                if is_enabled:
                    self.errmsg = 'Snmpd process is not in ps list.'           
                else:
                    self.errmsg = 'Snmpd process is still in ps list.'
            else:
                if is_enabled:
                    self.passmsg = 'Snmpd process is in ps list.'
                else:
                    self.passmsg = 'Snmpd process is not in ps list.'
        except Exception, ex:
            self.errmsg = ex.message    
        