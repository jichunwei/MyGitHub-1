'''
Dashboard
7.2.1.1    NA view all devices group in the network
7.3.1.1    GA view his own devices group in the network
7.4.1.1    GO view his own devices group in the network

NOTE:
. user must be deleted before device groups this is due to the feature
  "assign group owners"

config
. delete all del-able users/device groups
. create the test user (na, ga, go, op)
. create device groups (one or more)
. assign device groups to test user (in ga, go, op cases)
. create and login to fm by test user
test
. get all the devices on dashboard
. and make sure the info is correct:
  . na: see them all
  . ga, go: see what they own
  . op: see nothing (exception raise!)
clean up
. delete all del-able users/device groups
'''
import logging
from pprint import pformat

from RuckusAutoTest.tests.fm.lib_FM import init_coms, log_trace, log_cfg
from RuckusAutoTest.components import create_com

from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib import dev_features as ft
from RuckusAutoTest.models import Test

fmft = ft.FM

'''
. is_db_accessible is True by default, this indicates the exception is not raise
  (refer to op case)
. assign_group config is calc from dev_groups, test_user
. dev_groups: matches based on model only (for now)
'''
testcase = 1
test_cfg = [
    dict(
        dev_groups=[
            dict(groupname='dg_2942', matches=[dict(model='zf2942')],),
            dict(groupname='dg_7942', matches=[dict(model='zf7942')],),
        ],
        test_user=dict(
            username='na',   role=fmft.roles['network_admin'],
            password='user', confirm_password='user',
        ),
        #is_db_accessible=True,
    ),
    dict(
        dev_groups=[
            dict(groupname='dg_2942', matches=[dict(model='zf2942')],),
            dict(groupname='dg_7942', matches=[dict(model='zf7942')],),
        ],
        test_user=dict(
            username='ga',   role=fmft.roles['group_admin'],
            password='user', confirm_password='user',
        ),
    ),
    dict(
        dev_groups=[
            dict(groupname='dg_2942', matches=[dict(model='zf2942')],),
            dict(groupname='dg_7942', matches=[dict(model='zf7942')],),
        ],
        test_user=dict(
            username='go',   role=fmft.roles['group_op'],
            password='user', confirm_password='user',
        ),
    ),
][testcase]


class FM_DA_ViewDevices(Test):
    def config(self, cfg):
        self.errmsg = self.passmsg = ''
        self._cfg_test_params(cfg)
        lib.fm.user.delete_all(self.fm)
        lib.fm.da.delete_all(self.fm)

        self._create_user(self.fm, self.p['test_user'])
        self._create_dev_groups()

        if self.p['test_user']['role'] != fmft.roles['network_admin']:
            self._assign_dev_groups(self.fm, self.p['assign_group'])

        self._create_n_login_fm()


    def test(self):
        self._get_dashboard_total_devices()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._test_results()
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
        if not 'is_db_accessible' in self.p:
            self.p['is_db_accessible'] = True
        self.p['assign_group'] = dict(
            username=self.p['test_user']['username'],
            groupnames=[dg['groupname'] for dg in self.p['dev_groups']],
        )
        init_coms(self,dict(tb=self.testbed,))
        # no need to update password, browser_type, refer to _create_n_login_fm()
        self.p['fm_cfg'] = self.fm.get_cfg()
        self.p['fm_cfg'].update(dict(
            username=self.p['test_user']['username'],
            password=self.p['test_user']['password'],
        ))

        self._calc_total_devices()
        logging.debug('Test Configs:\n%s' % pformat(self.p))


    def _create_user(self, fm, cfg):
        logging.info('Create an user: %s' % cfg['username'])
        log_cfg(cfg, 'user')
        lib.fm.user.add(fm, cfg)


    def _create_dev_group(self, dg_cfg):
        logging.info('Create a group: %s' % dg_cfg['groupname'])
        log_cfg(dg_cfg, 'dev_group')
        try:
            lib.fm.da.add(self.fm, dg_cfg)
        except:
            log_trace()


    def _create_dev_groups(self):
        logging.info('Create device groups')
        log_cfg(self.p['dev_groups'], 'dev_groups')
        for dg in self.p['dev_groups']:
            self._create_dev_group(dg)


    def _assign_dev_groups(self, fm, cfg):
        logging.info('Assign groups to user')
        log_cfg(cfg)
        lib.fm.ga.assign(fm, cfg)


    def _get_dashboard_total_devices(self):
        logging.info('Get the total number of devices on dashboard')
        try:
            view = lib.fm.dashboard.get_view(self.p['fm'], fmft.predef_views['aps'])
            self.p['db_total_devices'] = int(view['conn']) + int(view['disconn'])
            log_cfg(self.p['db_total_devices'], 'db_total_devices')
            if not self.p['is_db_accessible']:
                self.errmsg = 'Able to get total devices on dashboard'
        except:
            log_trace()
            if self.p['is_db_accessible']:
                self.errmsg = 'Unable to get total devices on Dashboard'


    def _test_results(self):
        '''
        . if not dashboard not accessible then return pass
        . else compare the total device numbers and return accordingly
        '''
        if not self.p['is_db_accessible']:
            self.passmsg = 'Unable to get total devices on Dashboard'
            return

        logging.info('Compare the total devices from testbed/dashboard')
        if self.p['tb_total_devices'] != self.p['db_total_devices']:
            self.errmsg = 'Number of devices mismatch: Dashboard=%s, Testbed=%s' % \
                (self.p['db_total_devices'], self.p['tb_total_devices'])
            return
        self.passmsg = 'The number of devices displayed correctly'
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


    def _calc_total_devices(self):
        '''
        . calc the total numbers of devices based on the testbed
        . this is called during configuring test params
        '''
        logging.info('Calculate the total number of devices')
        if self.p['test_user']['role'] == fmft.roles['network_admin']:
            self.p['tb_total_devices'] = len(self.aps)
            return

        models = [dg['matches'][0]['model'] for dg in self.p['dev_groups']]
        log_cfg(models, 'models')
        devs = []
        for m in models:
            devs.extend(self.tb.get_ap_by_model(m))
        log_cfg(devs, 'devs')
        self.p['tb_total_devices'] = len(devs)


