'''
7.2.4 Provisioning
7.2.4.1    NA create Configuration Upgrade task for all device groups
7.2.4.2    NA create Factory Reset task for all device groups
7.2.4.3    NA create ZD Clone task for all device groups
7.2.4.4    NA upgrade firmware for all device groups
7.2.4.5    NA create Reboot task for all device groups

7.3.4 Provisioning
7.3.4.1    GA create Configuration Upgrade task for his own device groups
7.3.4.2    GA create Factory Reset task for his own device groups
7.3.4.3    GA upgrade firmware for his own device groups
7.3.4.4    GA create Reboot task for his own device groups
7.3.4.5    GA can not upload firmware to FM server

7.4.4 Provisioning
7.4.4.1    GO can not create template
7.4.4.2    GO can not create Configuration Upgrade task
7.4.4.3    GO can not create Firmware Upgrade task

NOTE:
. user must be deleted before device group deletion this is due to the feature
  "assign group owners"

config
. delete all del-able users/device groups
. create the test user (na)
. create device groups (one or more)
. assign device groups to test user
. create and login to fm by test user
test
. create a provisioning task, wait for run completion and make sure it is successful
. and make sure the result as expected
  . na: everything works fine
clean up
. delete all del-able users/device groups
'''
import logging
from pprint import pformat

from RuckusAutoTest.common.utils import log_trace, log_cfg, get_unique_name
from RuckusAutoTest.tests.fm.lib_FM import init_coms, create_fm
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib import dev_features as ft
from RuckusAutoTest.models import Test

fmft = ft.FM

'''
. is_create is True by default
. is_tmpl_create is True by default
. testcase = cfg_upgrade, factory_reset, zd_clone, fw_upgrade, reboot
'''
testcase = 11
test_cfg = [
    dict(
        testcase='fw_upgrade',
        user=dict(
            username='na',   role=fmft.roles['network_admin'],
            password='user', confirm_password='user',
        ),
        dev_groups=[dict(groupname='dg_2942', matches=[dict(model='zf2942')],),],
        task=dict(
            task_name='2942', schedule='now',
            zf2942_fw='.*8.1.0.0.124.*', # get this by model
            device=['192.168.20.180'], # get this by model
        ),
    ),
    dict(
        testcase='factory_reset',
        user=dict(
            username='na',   role=fmft.roles['network_admin'],
            password='user', confirm_password='user',
        ),
        dev_groups=[dict(groupname='dg_2942', matches=[dict(model='zf2942')],),],
        task=dict(
            task_name='2942', schedule='now', reboot='True',
            device=['192.168.20.180'], # get this by model
        ),
    ),
    dict(
        testcase='ap_reboot',
        user=dict(
            username='na',   role=fmft.roles['network_admin'],
            password='user', confirm_password='user',
        ),
        dev_groups=[dict(groupname='dg_2942', matches=[dict(model='zf2942')],),],
        task=dict(
            task_name='2942', schedule='now',
            device=['192.168.20.180'], # get this by model
        ),
    ),
    dict(
        testcase='cfg_upgrade',
        user=dict(
            username='na',   role=fmft.roles['network_admin'],
            password='user', confirm_password='user',
        ),
        dev_groups=[
            dict(groupname='dg_2942', matches=[dict(model='zf2942')],),
        ],
        tmpl=dict( # for cfg_upgrade only
            template_name='t_2942', template_model='zf2942',
            options=dict(device_general=dict(device_name='superdog'))
        ),
        task=dict(
            task_name='2942',
            #template_name='', # update later
            template_model='zf2942'.upper(),
            provision_to=dict(device='192.168.20.180'), # get this by model
        ),
    ),

    # -- GA
    dict(
        testcase='fw_upgrade',
        user=dict(
            username='ga',   role=fmft.roles['group_admin'],
            password='user', confirm_password='user',
        ),
        dev_groups=[dict(groupname='dg_2942', matches=[dict(model='zf2942')],),],
        task=dict(
            task_name='2942', schedule='now',
            zf2942_fw='.*8.2.0.0.13.*', # get this by model
            device=['192.168.20.180'], # get this by model
        ),
    ),
    dict(
        testcase='factory_reset',
        user=dict(
            username='ga',   role=fmft.roles['group_admin'],
            password='user', confirm_password='user',
        ),
        dev_groups=[dict(groupname='dg_2942', matches=[dict(model='zf2942')],),],
        task=dict(
            task_name='2942', schedule='now', reboot='True',
            device=['192.168.20.180'], # get this by model
        ),
    ),
    dict(
        testcase='ap_reboot',
        user=dict(
            username='ga',   role=fmft.roles['group_admin'],
            password='user', confirm_password='user',
        ),
        dev_groups=[dict(groupname='dg_2942', matches=[dict(model='zf2942')],),],
        task=dict(
            task_name='2942', schedule='now',
            device=['192.168.20.180'], # get this by model
        ),
    ),
    dict(
        testcase='cfg_upgrade',
        user=dict(
            username='ga',   role=fmft.roles['group_admin'],
            password='user', confirm_password='user',
        ),
        dev_groups=[
            dict(groupname='dg_2942', matches=[dict(model='zf2942')],),
        ],
        tmpl=dict( # for cfg_upgrade only
            template_name='t_2942', template_model='zf2942',
            options=dict(device_general=dict(device_name='superdog'))
        ),
        task=dict(
            task_name='2942',
            #template_name='', # update later
            template_model='zf2942'.upper(),
            provision_to=dict(device='192.168.20.180'), # get this by model
        ),
    ),

    # -- GO
    dict(
        testcase='fw_upgrade',
        user=dict(
            username='go',   role=fmft.roles['group_op'],
            password='user', confirm_password='user',
        ),
        dev_groups=[dict(groupname='dg_2942', matches=[dict(model='zf2942')],),],
        task=dict(
            task_name='2942', schedule='now',
            zf2942_fw='.*8.2.0.0.13.*', # get this by model
            device=['192.168.20.180'], # get this by model
        ),
        is_create=False,
    ),
    dict(
        testcase='factory_reset',
        user=dict(
            username='go',   role=fmft.roles['group_op'],
            password='user', confirm_password='user',
        ),
        dev_groups=[dict(groupname='dg_2942', matches=[dict(model='zf2942')],),],
        task=dict(
            task_name='2942', schedule='now', reboot='True',
            device=['192.168.20.180'], # get this by model
        ),
        is_create=False,
    ),
    dict(
        testcase='ap_reboot',
        user=dict(
            username='go',   role=fmft.roles['group_op'],
            password='user', confirm_password='user',
        ),
        dev_groups=[dict(groupname='dg_2942', matches=[dict(model='zf2942')],),],
        task=dict(
            task_name='2942', schedule='now',
            device=['192.168.20.180'], # get this by model
        ),
        is_create=False,
    ),
    dict(
        testcase='cfg_upgrade',
        user=dict(
            username='go',   role=fmft.roles['group_op'],
            password='user', confirm_password='user',
        ),
        dev_groups=[
            dict(groupname='dg_2942', matches=[dict(model='zf2942')],),
        ],
        tmpl=dict( # for cfg_upgrade only
            template_name='t_2942', template_model='zf2942',
            options=dict(device_general=dict(device_name='superdog'))
        ),
        task=dict(
            task_name='2942',
            #template_name='', # update later
            template_model='zf2942'.upper(),
            provision_to=dict(device='192.168.20.180'), # get this by model
        ),
        is_create=False,
    ),
][testcase]
#
#'''
#device, *_fw: get these from user input
#'''
#TASK_TMPL = dict(
#    ap_reboot=dict(
#        task_name='%s', schedule='now', device=[],
#    ),
#    factory_reset=dict(
#        task_name='%s', schedule='now', device=[],
#        reboot='True',
#    ),
#    fw_upgrade=dict(
#        task_name='%s', schedule='now', device=[],
#        zf2942_fw='.*8.1.0.0.124.*',
#    ),
#    cfg_upgrade=dict(
#        task_name='%s',
#        template_model='zf2942'.upper(), #template_name='', # update later
#        provision_to=dict(device='192.168.20.180'), # get this by model
#    )
#)
#
#dev_groups=[dict(groupname='dg_2942', matches=[dict(model='zf2942')],),]
#
#tmpl=dict( # for cfg_upgrade only
#    template_name='t_2942', template_model='zf2942',
#    options=dict(device_general=dict(device_name='superdog'))
#)
#
#
#def get_task(task_type, dgs):
#    '''
#    . dgs: (device groups) a list of device IPs
#    '''
#    task = copy.deepcopy(TASK_TMPL[task_type])
#    task['task_name'] = 'dg'
#    task['device'] = dgs
#
#
#def get_user(role):
#    return dict(
#        username='na',   role=fmft.roles['network_admin'],
#        password='user', confirm_password='user',
#    )


class FM_DA_Provisioning(Test):
    def config(self, cfg):
        self.errmsg = self.passmsg = ''
        self._cfg_test_params(cfg)
        lib.fm.user.delete_all(self.fm)
        lib.fm.da.delete_all(self.fm)

        lib.fm.user.add(self.fm, self.p['user'])
        self._create_dev_groups()

        if self.p['user']['role'] != fmft.roles['network_admin']:
            lib.fm.ga.assign(self.fm, self.p['assign_group'])

        self.p['fm'] = create_fm(self.p['fm_cfg'], self.tb.selenium_mgr)


    def test(self):
        self._create_task()
        if not self.p['is_create']:
            if self.errmsg:
                return ('PASS', self.errmsg)
            else:
                return ('FAIL', 'Task can be created')
        if self.errmsg: return ('FAIL', self.errmsg)

        self._monitor_task()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)


    def cleanup(self):
        if 'fm' in self.p:
            del self.p['fm']
        if 'tmpl' in self.p and self.p['is_create']:
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
        if not 'is_create' in self.p: self.p['is_create'] = True
        if not 'is_tmpl_create' in self.p: self.p['is_tmpl_create'] = True

        self.p['assign_group'] = dict(
            username=self.p['user']['username'],
            groupnames=[dg['groupname'] for dg in self.p['dev_groups']],
        )
        init_coms(self,dict(tb=self.testbed,))

        # no need to update password, browser_type, refer to _create_n_login_fm()
        self.p['fm_cfg'] = self.fm.get_cfg()
        self.p['fm_cfg'].update(dict(
            username=self.p['user']['username'],
            password=self.p['user']['password'],
            #password=self.p['user']['password'],
        ))

        # task lib and task print message
        self.lib, self.p['taskmsg'] = dict(
            cfg_upgrade=  (lib.fm.cfg_upgr, 'Config Upgrade'),
            factory_reset=(lib.fm.fr, 'Factory Reset'),
            fw_upgrade=   (lib.fm.fwup, 'Firmware Upgrade'),
            ap_reboot=    (lib.fm.ap_reboot, 'AP Reboot'),
            zd_clone=     (lib.fm.zd_cloning, 'ZD Clone'),
        )[self.p['testcase']]

        self.p['task']['task_name'] = get_unique_name(self.p['task']['task_name'])
        self.p['taskmatch'] = dict( task_name=self.p['task']['task_name'] )

        if 'tmpl' in self.p:
            self.p['tmpl']['template_name'] = get_unique_name(self.p['tmpl']['template_name'])
            self.p['task']['template_name'] = self.p['tmpl']['template_name']

        logging.debug('Test Configs:\n%s' % pformat(self.p))


    def _create_dev_group(self, cfg):
        logging.info('Create a group: %s' % cfg['groupname'])
        log_cfg(cfg, 'dev_group')
        try:
            lib.fm.da.add(self.fm, cfg)
        except:
            log_trace()


    def _create_dev_groups(self):
        logging.info('Create device groups')
        log_cfg(self.p['dev_groups'], 'dev_groups')
        for dg in self.p['dev_groups']:
            self._create_dev_group(dg)


    def _create_tmpl(self):
        '''
        . try to create the config template
        '''
        logging.info('Create a template')
        log_cfg(self.p['tmpl'])
        try:
            lib.fm.cfg_tmpl.create_cfg_tmpl(self.p['fm'], self.p['tmpl'])
        except:
            log_trace()
            self.errmsg = 'Failed to create an Template for Config Upgrade'


    def _create_cfg_upgrade(self):
        if self.p['is_tmpl_create']:
            self._create_tmpl()
        self.p['task'].update({'obj':self.p['fm']})
        logging.info('Create %s task' % self.p['taskmsg'])
        log_cfg(self.p['task'], 'task')
        try:
            self.lib.create_task(**self.p['task'])
        except:
            log_trace()
            self.errmsg = 'Failed to create %s task' % self.p['taskmsg']
            self.p['task'].pop('obj')
            return
        self.p['task'].pop('obj')
        self.passmsg = 'Able to create %s task' % self.p['taskmsg']


    def _create_task(self):
        if self.p['testcase'] == 'cfg_upgrade':
            return self._create_cfg_upgrade()

        logging.info('Create %s task' % self.p['taskmsg'])
        log_cfg(self.p['task'], 'task')
        try:
            self.lib.create_task(self.p['fm'], self.p['task'])
        except:
            log_trace()
            self.errmsg = 'Failed to create %s task' % self.p['taskmsg']


    def _monitor_task(self):
        if self.p['testcase'] == 'cfg_upgrade':
            return

        logging.info('Monitor %s task' % self.p['taskmsg'])
        log_cfg(self.p['taskmatch'], 'taskmatch')
        try:
            self.lib.monitor_task(self.p['fm'], self.p['taskmatch'])
        except:
            log_trace()
            self.errmsg = 'Failed to monitor %s task' % self.p['taskmsg']
            return
        self.passmsg = 'Able to create %s task' % self.p['taskmsg']

