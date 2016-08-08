'''
Admin testcases:
+ special char check
  > make sure special chars can not be put in

config
. delete all del-able users
test
. create user with special chars
. make sure the user cannot be created
clean up
. delete created users
'''

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.tests.fm.lib_FM import *
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib import dev_features as ft
from RuckusAutoTest.models import Test

fmft = ft.FM
'''
The following characters are not allowed:
  < > ~ ! # $ % ^ * / \ ( ) ? , : ; ' ` "
Allowed: user_@&_+|=-}{][
'''

testcase = 0
test_cfg = [
    dict(
        user=dict(
            username=r'user_<>~!#$%^*/\()?,:;\'`"',
            password='user',
            confirm_password='user',
            role=fmft.roles['network_admin'],
        ),
        is_create=False,
    ),
    dict(
        user=dict(
            username=r'[{-@=&|+_+|&=@-}]',
            password='user',
            confirm_password='user',
            role=fmft.roles['network_admin'],
        ),
        is_create=True,
    ),
][testcase]


class FM_AdminUserSpecialChars(Test):
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
        try:
            lib.fm.user.add(self.fm, self.p['user'])
        except:
            log_trace()
            if not self.p['is_create']:
                return
            self.errmsg = 'Unable to create user: %s' % self.p['user']['username']


    def _test_user(self):
        '''
        . find the user on user list
        . return accordingly
        '''
        user = self.p['user']['username']
        lib.fm.user.nav_to(self.fm, force=True) # avoid side effect
        self.passmsg, self.errmsg = {
            (True,True):  ('User (%s) is created successfully' % user, ''),
            (False,False):('User (%s) is not created' % user, ''),
            (False,True): ('', 'Cannot create user (%s)' % user),
            (True,False): ('', 'User (%s) is created' % user),
        }[(True if lib.fm.user.find(self.fm, dict(username=user)) else False,
           self.p['is_create'])]
        '''
        if lib.fm.user.find(self.fm, dict(user=user)):
            if self.p['is_create']:
                self.passmsg = 'User (%s) is created successfully' % user
                return
            self.errmsg = 'Cannot create user (%s)' % user
            return
        if not self.p['is_create']:
            self.passmsg = 'User (%s) is not created' % user
            return
        self.errmsg = 'User (%s) is created' % user
        return
        '''
