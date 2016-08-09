'''
west.li
only super/operator level user can do it
'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import zd_admin_privilage_level


class CB_ZD_Privilage_Level_Show_Block_Clients(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        res = self._user_level_behavior()
        
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
        
    def _user_level_behavior(self):
        return zd_admin_privilage_level.go_to_blocked_clients(self.zd,self.level)
     