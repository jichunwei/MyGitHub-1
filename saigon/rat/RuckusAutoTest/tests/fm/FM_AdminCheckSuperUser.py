'''
Admin testcases:
+ default super-user account
  > can change the pass
  > cannot delete this

config
. delete all del-able users
test
. get the default user on testbed
. get this user on the list and make sure there is no option delete
. edit the password of this user
. re-login with the new password in a new fm client
. make sure the script can log into fm with this default account

clean up
. change the password back (get the pass from testbed)
'''
import logging
from pprint import pformat

from RuckusAutoTest.common.utils import log_cfg, log_trace
from RuckusAutoTest.tests.fm.lib_FM import init_coms
from RuckusAutoTest.components import create_com
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib import dev_features as ft

from RuckusAutoTest.models import Test


fmft = ft.FM


class FM_AdminCheckSuperUser(Test):
    def config(self, cfg):
        self.errmsg = self.passmsg = ''
        self._cfg_test_params(cfg)
        lib.fm.user.delete_all(self.fm)


    def test(self):
        self._get_acc_info()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._check_deleting_acc()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._edit_acc(self.p['acc'])
        if self.errmsg: return ('FAIL', self.errmsg)

        self._test_relogin_fm()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', 'Cannot delete default account but can change its password')


    def cleanup(self):
        self._edit_acc(self.p['default_acc'])
        lib.fm.user.delete_all(self.fm)
        self.fm.logout()


    def _cfg_test_params(self, cfg):
        self.p = cfg
        #self.p = test_cfg
        init_coms(self,dict(tb=self.testbed,))
        logging.debug('Test Configs:\n%s' % pformat(self.p))


    def _get_acc_info(self):
        logging.info('Get the account info from testbed > Flex Master')
        fm_cfg = self.p['fm_cfg'] = self.fm.get_cfg()
        log_cfg(self.p['fm_cfg'], 'fm_cfg')
        self.p['default_acc'] = dict(
            password=fm_cfg['password'],
            confirm_password=fm_cfg['password'],
        )
        self.p['username'] = fm_cfg['username']
        log_cfg(self.p, 'self.p')


    def _check_deleting_acc(self):
        '''
        . iterate through acc table by super-account-name
        . and make sure there is no 'delete' in 'action'
        '''
        user = self.p['username']
        logging.info('Trying to delete the default super-user account: %s' % user)
        tbl_cfg = dict(get='iter',match=dict(username=user), op='eq')

        for r in lib.fm.user.get_tbl(self.fm, 'tbl', tbl_cfg):
            if 'delete' in r['row']['action'].lower():
                self.errmsg = 'Default user (%s) can be deleted' % user
                return
            else:
                return # success case
        self.errmsg = 'Cannot find user (%s) on user list' % user


    def _edit_acc(self, cfg):
        user = self.p['username']
        logging.info('Edit the default account: %s' % user)
        mcfg = dict(username=user)
        try:
            lib.fm.user.edit(self.fm, mcfg, cfg)
        except:
            log_trace()
            self.errmsg = 'Fail to edit the account: %s' % user


    def _test_relogin_fm(self):
        self.p['fm_cfg'].update(dict(
            password=self.p['acc']['password']),
            browser_type='firefox',
        ) # hack a bit
        logging.info('Create and login to FM with given account: %s' % \
                     self.p['fm_cfg']['username'])
        try:
            fm=create_com('fm', self.p['fm_cfg'], self.tb.selenium_mgr, https=False)
            fm.start()
            fm.stop()
            del fm
        except:
            log_trace()
            self.errmsg = 'Cannot login with this account'
            return
        return


