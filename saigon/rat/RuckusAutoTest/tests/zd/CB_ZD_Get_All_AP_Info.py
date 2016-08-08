'''
louis@ruckuswireless.com
get all AP information on ZD GUI
    
'''

from RuckusAutoTest.models import Test

class CB_ZD_Get_All_AP_Info(Test):
    '''
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        self.all_ap_info_on_zd = self.zd.get_all_ap_info()
        self._update_carrier_bag()
        
        return self.returnResult("PASS", passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['all_ap_info_on_zd'] = self.all_ap_info_on_zd
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''
        self.passmsg = ''
    
