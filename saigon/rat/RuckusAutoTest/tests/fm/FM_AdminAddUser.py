'''
Admin testcases:
+ super user/oper added
  > make sure acc can be created

config
. delete all del-able users
test
. create user according user type
. check to see if user exists
clean up
. delete created user
'''

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.tests.fm.lib_FM import *
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib import dev_features as ft
from RuckusAutoTest.models import Test

fmft = ft.FM

testcase = 0
test_cfg = [
    dict(
        user=dict(
            username='na',
            password='user',
            confirm_password='user',
            role=fmft.roles['network_admin'],
        ),
    ),
    dict(
        user=dict(
            username='ga',
            password='user',
            confirm_password='user',
            role=fmft.roles['group_admin'],
        ),
    ),
    dict(
        user=dict(
            username='go',
            password='user',
            confirm_password='user',
            role=fmft.roles['group_op'],
        ),
    ),
    dict(
        user=dict(
            username='do',
            password='user',
            confirm_password='user',
            role=fmft.roles['device_op'],
        ),
    ),
][testcase]


class FM_AdminAddUser(Test):
    def config(self, cfg):
        self.errmsg = self.passmsg = ''
        self._cfg_test_params(cfg)
        lib.fm.user.delete_all(self.fm)


    def test(self):
        self._create_user()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._test_user()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)


    def cleanup(self):
        lib.fm.user.delete_all(self.fm)
        self.fm.logout()


    def _cfg_test_params(self, cfg):
        self.p = cfg
        #self.p = test_cfg
        init_coms(self,dict(tb=self.testbed,))
        logging.debug('Test Configs:\n%s' % pformat(self.p))


    def _create_user(self):
        logging.info('Create an user: %s' % self.p['user']['username'])
        log_cfg(self.p['user'], 'user')
        lib.fm.user.add(self.fm, self.p['user'])


    def _test_user(self):
        '''
        . find the user on user list
        . return accordingly
        '''
        username = self.p['user']['username']
        lib.fm.user.nav_to(self.fm, force=True) # avoid side effect
        if lib.fm.user.find(self.fm, dict(username=username)):
            self.passmsg = 'User (%s) is created successfully' % username
            return
        self.errmsg = 'Cannot find user (%s) in user list' % username
        return
