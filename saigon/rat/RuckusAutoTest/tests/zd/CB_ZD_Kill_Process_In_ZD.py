'''
Description:kill process in zd shell
Created on 2013 3 4
@author: West.li
'''
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import shell_mode_functions as zd_shell

class CB_ZD_Kill_Process_In_ZD(Test):
    '''
    Check from ZDCLI, just verify APs number.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):        
        zd_shell.kill_process(self.zdcli, self.process_name)
        self._update_carrier_bag()
        return self.returnResult('PASS', 'process %s kill successfully' % self.process_name)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf= dict(timeout = 1800,
                        process_name = '')
        self.conf.update(conf)        
        self.timeout = self.conf['timeout']  
        self.process_name = self.conf['process_name']      
        if self.testbed.components.has_key('ZoneDirectorCLI'):                            
            self.zdcli = self.testbed.components['ZoneDirectorCLI'] 
        if self.carrierbag.has_key('active_zd_cli'):
            self.zdcli = self.carrierbag['active_zd_cli']
        if self.conf.get('zdcli'):
            self.zdcli = self.carrierbag[self.conf['zdcli']]
        self.passmsg = ""
        self.errmsg = ""   
    
