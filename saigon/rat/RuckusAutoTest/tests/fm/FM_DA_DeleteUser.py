'''
config
. delete all del-able users
. create an account (ga - if required) and login by that account
. create tested account
test
. delete account
clean up
. delete all del-able users
'''

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.tests.fm.lib_FM import *
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib import dev_features as ft
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import create_com

fmft = ft.FM

testcase = 0
test_cfg = [
    dict(
        test_user=dict(
            username='na',
            password='user',
            confirm_password='user',
            role=fmft.roles['network_admin'],
        ),
    ),
    dict(
        test_user=dict(
            username='ga',
            password='user',
            confirm_password='user',
            role=fmft.roles['group_admin'],
        ),
    ),
    dict(
        test_user=dict(
            username='go',
            password='user',
            confirm_password='user',
            role=fmft.roles['group_op'],
        ),
    ),
    dict(
        test_user=dict(
            username='do',
            password='user',
            confirm_password='user',
            role=fmft.roles['device_op'],
        ),
    ),

    # -- GA
    dict(
        user=dict(
            username='ga',
            password='user',
            confirm_password='user',
            role=fmft.roles['group_admin'],
        ),
        test_user=dict(
            username='go',
            password='user',
            confirm_password='user',
            role=fmft.roles['group_op'],
        ),
    ),
    dict(
        user=dict(
            username='ga',
            password='user',
            confirm_password='user',
            role=fmft.roles['group_admin'],
        ),
        test_user=dict(
            username='do',
            password='user',
            confirm_password='user',
            role=fmft.roles['device_op'],
        ),
    ),

][testcase]


class FM_DA_DeleteUser(Test):
    def config(self, cfg):
        self.errmsg = self.passmsg = ''
        self._cfg_test_params(cfg)
        lib.fm.user.delete_all(self.fm)
        if 'user' in self.p:
            # use this account instead of default one
            self._create_user(self.fm, self.p['user'])
            self.p['fm_cfg'].update(dict(
                password=self.p['user']['password'],
                username=self.p['user']['username'],
            ))
        self._create_n_login_fm()

        if 'test_user' in self.p:
            if 'is_create_by_na' in self.p and self.p['is_create_by_na']:
                # for GO can't delete OP case
                self._create_user(self.fm, self.p['test_user'])
            else:
                self._create_user(self.p['fm'], self.p['test_user'])
        else:
            # user cannot delete himself cases
            self.p['test_user'] = copy.deepcopy(self.p['user'])


    def test(self):
        self._delete_user()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._test_user()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)


    def cleanup(self):
        if 'fm' in self.p:
            del self.p['fm']
        lib.fm.user.delete_all(self.fm)
        self.fm.logout()


    def _cfg_test_params(self, cfg):
        self.p = cfg
        #self.p = test_cfg
        # no need to update password, browser_type, refer to _create_n_login_fm()
        init_coms(self,dict(tb=self.testbed,))
        self.p['fm_cfg'] = self.fm.get_cfg()
        if 'is_delete' not in self.p:
            self.p['is_delete'] = True
        logging.debug('Test Configs:\n%s' % pformat(self.p))


    def _create_user(self, fm, cfg):
        logging.info('Create an user: %s' % cfg['username'])
        log_cfg(cfg, 'user')
        lib.fm.user.add(fm, cfg)


    def _delete_user(self):
        mcfg = dict(username=self.p['test_user']['username'])
        lib.fm.user.delete(self.p['fm'], mcfg)


    def _test_user(self):
        '''
        . find the user on user list
        . return accordingly
        '''
        username = self.p['test_user']['username']
        lib.fm.user.nav_to(self.fm, force=True) # avoid side effect

        self.passmsg, self.errmsg = {
            (True,True):  ('', 'User (%s) is found' % username),
            (False,False):('', 'User (%s) is not found' % username),
            (False,True): ('User (%s) is not found' % username, ''),
            (True,False): ('User (%s) is found' % username, ''),
        }[(True if lib.fm.user.find(self.fm, dict(username=username)) else False,
           self.p['is_delete'])]


    def _create_n_login_fm(self):
        self.p['fm_cfg'].update(dict(
            password=self.p['fm_cfg']['password'],
            browser_type='firefox',
        )) # hack a bit
        logging.info('Create and login to FM with given account: %s' % \
                     self.p['fm_cfg']['username'])
        self.p['fm']=create_com('fm', self.p['fm_cfg'], self.tb.selenium_mgr, https=False)
        self.p['fm'].start()

