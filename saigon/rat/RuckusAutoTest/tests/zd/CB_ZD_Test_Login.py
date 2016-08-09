'''

Description: This script is used to test whether can login ZD or not.

'''


import logging
import time

from RuckusAutoTest.models import Test


class CB_ZD_Test_Login(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._testLogin()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        if self.conf['restore_zd_user']:
            self.zd.username=self.username_bak
            self.zd.password=self.password_bak
        pass

    def _initTestParameters(self, conf):
        self.conf = {'login_name': '',
                     'login_pass': '',
                     'restore_zd_user':False,
                     'expected_fail':False}
        self.conf.update(conf)        
        self.zd = self.testbed.components['ZoneDirector']
        if self.conf.get('zd'):
            if self.conf['zd']=='active':
                self.zd = self.carrierbag['active_zd']
            elif self.conf['zd']=='standby':
                self.zd = self.carrierbag['standby_zd']
        self.username_bak=self.zd.username
        self.password_bak=self.zd.password
        self.errmsg = ''
        self.passmsg = ''

    def _testLogin(self):
        if self.conf['login_name']:
            self.zd.username = self.conf['login_name']
        
        if self.conf['login_pass']:
            self.zd.password = self.conf['login_pass']
        
        try:
            logging.info("Login with username [%s] and password [%s]" % (self.zd.username, self.zd.password))
            self.zd.login(force = True)
            time.sleep(5)
            if self.conf['expected_fail']:
                self.zd.s.open(self.zd.conf['url.dashboard'])
            time.sleep(5)
            if not self.zd.is_logged_in():
                if not self.conf['expected_fail']:
                    self.errmsg = 'Fail to login with username[%s] and password[%s]'%(self.zd.username, self.zd.password)
                else:
                    self.passmsg = 'Fail to login with username[%s] and password[%s] as expected' % (self.zd.username, self.zd.password)
            else:
                self.passmsg = 'Login with username[%s] and password[%s] successfully' % (self.zd.username, self.zd.password)
                    
        except Exception, ex:
            self.errmsg = 'Fail to login with username[%s] and password[%s]: %s' % (self.zd.username, self.zd.password, ex.message)

                