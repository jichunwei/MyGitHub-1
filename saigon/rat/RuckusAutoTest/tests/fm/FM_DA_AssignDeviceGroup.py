'''
NOTE:
. user must be deleted before device groups this is due to the feature
  "assign group owners"

config
. delete all del-able users/device groups
. create an account (ga - if required) and login by that account
. create device group
test
. assign device group to user
. check to see if device group is assigned or not (on main window)
clean up
. delete all del-able users/device groups
'''
import logging
from pprint import pformat

from RuckusAutoTest.common.utils import log_cfg, log_trace
from RuckusAutoTest.tests.fm.lib_FM import init_coms
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib import dev_features as ft
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import create_com

fmft = ft.FM

'''
assign_group config is calc from dev_group, test_user
'''
testcase = 0
test_cfg = [
    # -- NA
    dict(
        user=dict(
            username='na',   role=fmft.roles['network_admin'],
            password='user', confirm_password='user',
        ),
        dev_group=dict(groupname='na_devgroup', matches=[dict(model='zf2942')],),
        test_user=dict(
            username='ga',   role=fmft.roles['group_admin'],
            password='user', confirm_password='user',
        ),
    ),
    dict(
        user=dict(
            username='na',   role=fmft.roles['network_admin'],
            password='user', confirm_password='user',
        ),
        dev_group=dict(groupname='na_devgroup', matches=[dict(model='zf2942')],),
        test_user=dict(
            username='go',   role=fmft.roles['group_op'],
            password='user', confirm_password='user',
        ),
    ),
    dict(
        user=dict(
            username='na',   role=fmft.roles['network_admin'],
            password='user', confirm_password='user',
        ),
        dev_group=dict(groupname='na_devgroup', matches=[dict(model='zf2942')],),
        test_user=dict(
            username='do',   role=fmft.roles['device_op'],
            password='user', confirm_password='user',
        ),
    ),
    # -- GA
    dict(
        user=dict(
            username='ga',   role=fmft.roles['group_admin'],
            password='user', confirm_password='user',
        ),
        dev_group=dict(groupname='ga_devgroup', matches=[dict(model='zf7942')],),
        test_user=dict(
            username='go',   role=fmft.roles['group_op'],
            password='user', confirm_password='user',
        ),
    ),
    dict(
        user=dict(
            username='ga',   role=fmft.roles['group_admin'],
            password='user', confirm_password='user',
        ),
        dev_group=dict(groupname='ga_devgroup', matches=[dict(model='zf7942')],),
        test_user=dict(
            username='do',   role=fmft.roles['device_op'],
            password='user', confirm_password='user',
        ),
    ),
][testcase]


class FM_DA_AssignDeviceGroup(Test):
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
        self._create_dev_group()
        if self.p['user']['role'] == fmft.roles['group_admin']:
            self.p['ga_assign_group'] = dict(
                username=self.p['user']['username'],
                groupnames=[self.p['dev_group']['groupname']],
            )
            log_cfg(self.p['ga_assign_group'])
            self._assign_dev_group(self.fm, self.p['ga_assign_group'])

        self._create_n_login_fm()
        self._create_user(self.p['fm'], self.p['test_user'])


    def test(self):
        self._assign_dev_group(self.p['fm'], self.p['assign_group'])
        if self.errmsg: return ('FAIL', self.errmsg)

        self._get_dev_group_assignment()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._test_dev_group_assignment()
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
        #self.p = test_cfg
        self.p['assign_group'] = dict(
            username=self.p['test_user']['username'],
            groupnames=[self.p['dev_group']['groupname']],
        )
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
        log_cfg(self.p['dev_group'], 'dev_group')
        try:
            lib.fm.da.add(self.fm, self.p['dev_group'])
        except:
            log_trace()


    def _assign_dev_group(self, fm, cfg):
        logging.info('Assign groups to user')
        log_cfg(cfg)
        lib.fm.ga.assign(fm, cfg)


    def _get_dev_group_assignment(self):
        logging.info('Get groups assignment')
        gn = self.p['assign_group']['groupnames'][0]
        user = self.p['assign_group']['username']
        self.p['fm_assign_group'] = \
            lib.fm.ga.get_assigned_groups(self.fm, user)
        #log_cfg(self.p['fm_assign_group'])
        self.p['fm_assign_group'] = [r['groupname'] for r in self.p['fm_assign_group']]
        log_cfg(self.p['fm_assign_group'])


    def _test_dev_group_assignment(self):
        '''
        . find the dg on dg list
        . return accordingly
        '''
        logging.info('Compare the device group assignment')
        r = self.p['fm_assign_group']
        e = self.p['assign_group']['groupnames']

        if not len(r) and not len(e):
            self.errmsg = 'There was no group assigned'
            return

        not_in_r = list(set(e)- set(r))
        if not_in_r:
            self.errmsg = 'These device groups are not assigned - %s' % not_in_r
            return
        not_in_e = list(set(r)- set(e))
        if not_in_e:
            self.errmsg = 'These device groups are not assigned but are in the list - %s' % not_in_e
            return
        self.passmsg = 'The device assignment works correctly'
        return


    def _create_n_login_fm(self):
        self.p['fm_cfg'].update(dict(
            password=self.p['fm_cfg']['password'],
            browser_type='firefox',
        )) # hack a bit
        logging.info('Create and login to FM with given account: %s' % \
                     self.p['fm_cfg']['username'])
        self.p['fm']=create_com('fm', self.p['fm_cfg'], self.tb.selenium_mgr, https=False)
        self.p['fm'].start()
