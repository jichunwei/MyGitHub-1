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
        create_user=dict( # for creating acc
            username='na',
            password='user',
            confirm_password='user',
            role=fmft.roles['network_admin'],
        ),
        user=dict( # for updating acc
            #username='', # un-change-able
            password='user1',
            confirm_password='user1',
            role=fmft.roles['device_op'],
        ),
    ),
][testcase]


class FM_DA_EditUser(Test):
    def config(self, cfg):
        self.errmsg = self.passmsg = ''
        self._cfg_test_params(cfg)
        lib.fm.user.delete_all(self.fm)
        self._create_user(self.fm, self.p['create_user'])


    def test(self):
        self._edit_user()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._test_login_user()
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
        self.p['fm_cfg'].update(dict(
            password=self.p['user']['password'],
            username=self.p['create_user']['username'],
        ))
        logging.debug('Test Configs:\n%s' % pformat(self.p))


    def _create_user(self, fm, cfg):
        logging.info('Create an user: %s' % cfg['username'])
        log_cfg(cfg, 'user')
        lib.fm.user.add(fm, cfg)


    def _test_user(self):
        '''
        . find the user on user list
        . get role and make sure role is up 2 date
        '''
        username = self.p['test_user']['username']
        lib.fm.user.nav_to(self.fm, force=True) # avoid side effect


    def _create_n_login_fm(self):
        self.p['fm_cfg'].update(dict(
            password=self.p['fm_cfg']['password'],
            browser_type='firefox',
        )) # hack a bit
        logging.info('Create and login to FM with given account: %s' % \
                     self.p['fm_cfg']['username'])
        self.p['fm']=create_com('fm', self.p['fm_cfg'], self.tb.selenium_mgr, https=False)
        self.p['fm'].start()


    def _test_login_user(self):
        try:
            self._create_n_login_fm()
            self.passmsg = 'Change user info successfully'
        except:
            log_trace()
            self.errmsg = 'Cannot login with this account: %s' % \
                          self.p['create_user']['username']
            return


    def _edit_user(self):
        user = self.p['create_user']['username']
        logging.info('Edit the default account: %s' % user)
        mcfg = dict(username=user)
        lib.fm.user.edit(self.fm, mcfg, self.p['user'])

