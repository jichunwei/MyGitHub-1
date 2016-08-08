'''
west.li
only super level user can do it
'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import zd_admin_privilage_level
import libZD_TestConfig as tconfig




class CB_ZD_Privilage_Level_Set_AP_Channalization(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        res = self._user_behavior_verify()
        
        if not res: 
            return self.returnResult('FAIL','the user behavior is not the same to expected')
        
        return self.returnResult('PASS', 'the user behavior is the same to expected')

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'level':'monitor',
                     'ap_mac':'',
                     'ap_tag':''}
        self.conf.update(conf)
        self.level=self.conf['level']
        self.zd = self.testbed.components['ZoneDirector']
        #@author: yuyanan @since: 2014-8-28 optimize: get ap mac from ap tag
        if self.conf.get('ap_tag'):
            self.mac = tconfig.get_active_ap_mac(self.testbed,self.conf['ap_tag'])
        else:
            self.mac = self.conf['ap_mac']
        self.errmsg = ''
        self.passmsg = ''
        
    def _user_behavior_verify(self):
        return zd_admin_privilage_level.set_ap_channelization(self.zd,self.mac)
     