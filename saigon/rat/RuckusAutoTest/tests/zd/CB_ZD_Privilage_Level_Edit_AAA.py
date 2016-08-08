'''
west.li
only super level user can do it
'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import zd_admin_privilage_level


class CB_ZD_Privilage_Level_Edit_AAA(Test):
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
                     'server_name':''}
        self.conf.update(conf)
        self.level=self.conf['level']
        self.zd = self.testbed.components['ZoneDirector']
        self.server_name = self.conf['server_name']
        self.errmsg = ''
        self.passmsg = ''
        
    def _user_behavior_verify(self):
        return zd_admin_privilage_level.edit_aaa_server(self.zd,self.level,self.server_name)
     