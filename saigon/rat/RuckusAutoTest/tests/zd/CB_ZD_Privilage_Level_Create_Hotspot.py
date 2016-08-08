'''
west.li
only super level user can do it
'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import zd_admin_privilage_level


class CB_ZD_Privilage_Level_Create_Hotspot(Test):
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
        self.conf = {'level':'monitor'}
        self.conf.update(conf)
        self.level=self.conf['level']
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''
        
    def _user_behavior_verify(self):
        return zd_admin_privilage_level.create_hotspot_cfg(self.zd,self.level)
     