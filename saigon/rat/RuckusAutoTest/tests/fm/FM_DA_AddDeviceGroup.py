'''
NOTE:
. user must be deleted before device groups this is due to the feature
  "assign group owners"

config
. delete all del-able users/device groups
. create an account (ga - if required) and login by that account
test
. create device group
. check to see if device group exists
clean up
. delete all del-able users/device groups
'''
import logging
from pprint import pformat

from RuckusAutoTest.common.utils import log_trace, log_cfg
from RuckusAutoTest.tests.fm.lib_FM import init_coms
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib import dev_features as ft
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import create_com

fmft = ft.FM

'''
cfg
. is_create = True if not set!
  this var is used to indicate the creation of dev_group
  in GA case, dev_group cannot be created
'''
testcase = 3
test_cfg = [
    # -- SA: creating
    dict(
        dev_group=dict(groupname='sa_devgroup',),
    ),
    # -- NA: creating
    dict(
        user=dict(
            username='na',   role=fmft.roles['network_admin'],
            password='user', confirm_password='user',
        ),
        dev_group=dict(groupname='na_devgroup',),
    ),
    # -- GA, GO, OP: NO creating
    dict(
        user=dict(
            username='ga',   role=fmft.roles['group_admin'],
            password='user', confirm_password='user',
        ),
        dev_group=dict(groupname='ga_devgroup',),
        is_create=False,
    ),
    # -- SA: assigning
    dict(
        dev_group=dict(groupname='sa_devgroup', matches=[dict(model='zf2942')],),
    ),
    # -- NA: assigning
    dict(
        user=dict(
            username='na',   role=fmft.roles['network_admin'],
            password='user', confirm_password='user',
        ),
        dev_group=dict(groupname='na_devgroup', matches=[dict(model='zf2942')],),
    ),
][testcase]


class FM_DA_AddDeviceGroup(Test):
    def config(self, cfg):
        self.errmsg = self.passmsg = ''
        self._cfg_test_params(cfg)
        lib.fm.user.delete_all(self.fm)
        lib.fm.da.delete_all(self.fm)
        if 'user' in self.p:
            # use this account instead of default one
            self._create_user(self.fm, self.p['user'])
            self.p['fm_cfg'].update(dict(
                password=self.p['user']['password'],
                username=self.p['user']['username'],
            ))
        self._create_n_login_fm()


    def test(self):
        self._create_dev_group()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._test_dev_group()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)


    def cleanup(self):
        if 'fm' in self.p:
            del self.p['fm']
        lib.fm.user.delete_all(self.fm)
        lib.fm.da.delete_all(self.fm)
        self.fm.logout()


    def _cfg_test_params(self, cfg):
        self.p = cfg
        self.p = test_cfg
        if 'is_create' not in self.p:
            self.p['is_create'] = True

        init_coms(self,dict(tb=self.testbed,))
        # no need to update password, browser_type, refer to _create_n_login_fm()
        self.p['fm_cfg'] = self.fm.get_cfg()
        logging.debug('Test Configs:\n%s' % pformat(self.p))


    def _create_user(self, fm, cfg):
        logging.info('Create an user: %s' % cfg['username'])
        log_cfg(cfg, 'user')
        lib.fm.user.add(fm, cfg)


    def _create_dev_group(self):
        logging.info('Create a group: %s' % self.p['dev_group']['groupname'])
        log_cfg(self.p['dev_group'], 'group')
        try:
            lib.fm.da.add(self.p['fm'], self.p['dev_group'])
        except:
            log_trace()


    def _test_dev_group(self):
        '''
        . find the dg on dg list
        . return accordingly
        '''
        gn = self.p['dev_group']['groupname']
        lib.fm.da.nav_to(self.fm, force=True) # avoid side effect
        self.passmsg, self.errmsg = {
            (True,  True):  ('Group is found',''),
            (False, False): ('Group is not found',''),
            (True,  False): ('','Group is found'),
            (False, True):  ('','Group is not found'),
        }[( True if lib.fm.da.find(self.fm, dict(groupname=gn)) else False,
            self.p['is_create'] )]


    def _create_n_login_fm(self):
        self.p['fm_cfg'].update(dict(
            password=self.p['fm_cfg']['password'],
            browser_type='firefox',
        )) # hack a bit
        logging.info('Create and login to FM with given account: %s' % \
                     self.p['fm_cfg']['username'])
        self.p['fm']=create_com('fm', self.p['fm_cfg'], self.tb.selenium_mgr, https=False)
        self.p['fm'].start()
