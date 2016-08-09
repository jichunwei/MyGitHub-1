'''
Inventory
7.2.2.1    NA create auto-configuration rule from all device groups
7.3.2.1    GA cannot create auto-configuration rule successfully
7.4.2.1    GO can not create auto-configuration rule from his own device groups

NOTE:
. user must be deleted before device groups this is due to the feature
  "assign group owners"

config
. delete all del-able users/device groups
. create the test user (na, ga, go)
. create device groups (one or more)
. assign device groups to test user (in ga, go cases)
. create and login to fm by test user
test
. create a template: exception might raise here!
. create an auto-config on inventory > device registration
. and make sure the assignment is correct
  . na: can create
  . ga, go: cannot
clean up
. delete all del-able users/device groups
'''
import logging
from pprint import pformat

from RuckusAutoTest.common.utils import log_cfg, log_trace, get_unique_name
from RuckusAutoTest.tests.fm.lib_FM import init_coms
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib import dev_features as ft
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import create_com

fmft = ft.FM

'''
. is_create is True by default
'''
testcase = 2
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
        tmpl=dict(
            template_name='t_2942', template_model='zf2942',
            options=dict(device_general=dict(device_name='superdog'))),
        rule=dict(cfg_rule_name='t_2942', device_group=fmft.predef_views['aps'], model='zf2942',
                  cfg_template_name='t_2942'),
        #is_create=True,
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
        tmpl=dict(
            template_name='t_2942', template_model='zf2942',
            options=dict(device_general=dict(device_name='superdog'))),
        rule=dict(cfg_rule_name='t_2942', device_group=fmft.predef_views['aps'], model='zf2942',
                  cfg_template_name='t_2942'),
        is_create=False,
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
        tmpl=dict(
            template_name='t_2942', template_model='zf2942',
            options=dict(device_general=dict(device_name='superdog'))),
        rule=dict(cfg_rule_name='t_2942', device_group=fmft.predef_views['aps'], model='zf2942',
                  cfg_template_name='t_2942'),
        is_create=False,
    ),
][testcase]


class FM_DA_CreateAutoCfg(Test):
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
        self._create_tmpl()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._create_auto_cfg_rule()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)


    def cleanup(self):
        if 'fm' in self.p:
            del self.p['fm']
        try:
            lib.fm.cfg_tmpl.delete_cfg_tmpl(self.fm, self.p['tmpl']['template_name'])
        except:
            log_trace()
        lib.fm.user.delete_all(self.fm)
        lib.fm.da.delete_all(self.fm)
        self.fm.logout()


    def _cfg_test_params(self, cfg):
        self.p = cfg
        #self.p = test_cfg
        if not 'is_create' in self.p:
            self.p['is_create'] = True

        self.p['assign_group'] = dict(
            username=self.p['test_user']['username'],
            groupnames=[dg['groupname'] for dg in self.p['dev_groups']],
        )
        init_coms(self,dict(tb=self.testbed,))
        # no need to update password, browser_type, refer to _create_n_login_fm()
        self.p['rule']['cfg_template_name'] = self.p['tmpl']['template_name'] = \
            get_unique_name(self.p['tmpl']['template_name'])
        self.p['rule']['cfg_rule_name'] = get_unique_name(self.p['rule']['cfg_rule_name'])

        self.p['fm_cfg'] = self.fm.get_cfg()
        self.p['fm_cfg'].update(dict(
            username=self.p['test_user']['username'],
            password=self.p['test_user']['password'],
        ))

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


    def _create_n_login_fm(self):
        self.p['fm_cfg'].update(dict(
            password=self.p['fm_cfg']['password'],
            browser_type='firefox',
        )) # hack a bit
        logging.info('Create and login to FM with given account: %s' % \
                     self.p['fm_cfg']['username'])
        self.p['fm']=create_com('fm', self.p['fm_cfg'], self.tb.selenium_mgr, https=False)
        self.p['fm'].start()


    def _create_tmpl(self):
        '''
        . try to create the config template
        '''
        logging.info('Create an Template')
        log_cfg(self.p['tmpl'])
        try:
            lib.fm.cfg_tmpl.create_cfg_tmpl(self.p['fm'], self.p['tmpl'])
            #if not self.p['is_create']:
            #    self.errmsg = 'Able to create the config template'
        except:
            log_trace()
            if self.p['is_create']:
                self.errmsg = 'Unable to create the config template'


    def _create_auto_cfg_rule(self):
        logging.info('Create an auto config rule')
        log_cfg(self.p['rule'])
        self.p['rule']['advance_return'] = True
        try:
            self.p['fm'].create_auto_cfg_rule(**self.p['rule'])
            if not self.p['is_create']:
                self.errmsg = 'Able to create auto config rule'
        except:
            log_trace()
            if self.p['is_create']:
                self.errmsg = 'Unable to create auto config rule'
        self.passmsg = 'The function works conrrectly'

