'''
west.li
all level user can ping ap
'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import zd_admin_privilage_level
import libZD_TestConfig as tconfig

class CB_ZD_Privilage_Level_Ping_AP(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        res=self._ping_ap()
        
        if not res: 
            return self.returnResult('FAIL', 'the user behavior is not the same to expected')
        
        return self.returnResult('PASS','the user behavior is the same to expected')

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'ap_mac':''}
        self.conf.update(conf)
        
        #@author: yuyanan @since: 2014-8-28 optimize: get ap mac from ap tag
        if self.conf.get('ap_tag'):
            self.ap_mac = tconfig.get_active_ap_mac(self.testbed,self.conf['ap_tag'])
        else:
            self.ap_mac = self.conf['ap_mac']
        
        self.zd = self.testbed.components['ZoneDirector']
        
    def _ping_ap(self):
        return zd_admin_privilage_level.ping_ap(self.zd,self.ap_mac)
     