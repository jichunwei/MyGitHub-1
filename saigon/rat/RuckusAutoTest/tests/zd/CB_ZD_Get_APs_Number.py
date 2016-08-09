'''
Description:get how many APs are managed at current ENV.
Created on 2011 12 25
@author: West.li
'''
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import scaling_zd_lib

class CB_ZD_Get_APs_Number(Test):
    '''
    Check from ZDCLI, just verify APs number.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):        
        self.ap_num = scaling_zd_lib.get_aps_num_from_cmd(self.zdcli,time_out = self.conf['timeout'])
        self._update_carrier_bag()
        return self.returnResult('PASS', '%d aps are managed by zd' % self.ap_num)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['managed_ap_num']=self.ap_num 
        pass
    
    def _init_test_params(self, conf):
        self.conf= dict(timeout = 1800)
        self.conf.update(conf)        
        self.timeout = self.conf['timeout']        
        if self.testbed.components.has_key('ZoneDirectorCLI'):                            
            self.zdcli = self.testbed.components['ZoneDirectorCLI'] 
        if self.carrierbag.has_key('active_zd_cli'):
            self.zdcli = self.carrierbag['active_zd_cli']
        if self.conf.get('zdcli'):
            self.zdcli = self.carrierbag[self.conf['zdcli']]
        self.passmsg = ""
        self.errmsg = ""   
    
