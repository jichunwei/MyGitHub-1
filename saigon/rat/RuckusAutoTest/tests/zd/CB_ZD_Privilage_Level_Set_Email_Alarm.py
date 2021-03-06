'''
west.li
only super level user can do it
'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import zd_admin_privilage_level


class CB_ZD_Privilage_Level_Set_Email_Alarm(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        res,msg = self._user_behavior_verify()
##### zj 2014-0305 zf-7694 optimization
        if not msg: 
            msg = 'no message.'
        if not res: 
            return self.returnResult('FAIL','the user behavior is not the same to expected. %s' % msg)
##### zj 2014-0305 zf-7694 optimization       
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
        return zd_admin_privilage_level.change_email_alarm_status(self.zd,self.level)
     