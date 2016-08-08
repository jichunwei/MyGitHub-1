
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import create_zd_by_ip_addr
#from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.components.NetgearL3Switch import NetgearL3Switch
#from RuckusAutoTest.components.lib.zd import redundancy_zd
#from RuckusAutoTest.components import Helper_ZD as zhlp

class CB_ZD_SR_Init_Env(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        msg = 'Initial Test Environment of Test'
        return self.returnResult('PASS', msg)
    
    def cleanup(self):
        pass

        
    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf = dict(
                       debug=False,
                       zd1_ip_addr = '192.168.0.2',
                       zd2_ip_addr = '192.168.0.3',
                       share_secret = 'testing',
                       )
        self.conf.update(conf)
                    
        self.carrierbag['zd1'] = self.testbed.components['zd1']
        self.carrierbag['zd2'] = self.testbed.components['zd2']                    
        self.carrierbag['zdcli1'] = self.testbed.components['ZDCLI1']
        self.carrierbag['zdcli2'] = self.testbed.components['ZDCLI2']
        self.carrierbag['share_secret'] = self.conf['share_secret']
        self.carrierbag['sw'] = self.testbed.components['L3Switch']
        self.carrierbag['disabled_ap_sw_port_list']=[]
        self.carrierbag['disabled_zd_sw_port_list']=[]
        
