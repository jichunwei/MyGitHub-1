'''
west.li
only super/operator level user can do it
'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import zd_admin_privilage_level


class CB_ZD_Privilage_Level_Select_Guest_Pass_Auth_Server(Test):
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
        self.conf = {'level':'monitor',
                     'server':''}
        self.conf.update(conf)
        self.level=self.conf['level']
        self.server=self.conf['server']
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''
        
    def _user_level_behavior(self):
        return zd_admin_privilage_level.select_guest_auth_server(self.zd,self.level,self.server)
     