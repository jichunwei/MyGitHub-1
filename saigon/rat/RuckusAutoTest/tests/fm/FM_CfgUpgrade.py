'''
Testsuite
1.1.9.2.1   Create new task to ZF2925
1.1.9.2.2   Create new task to ZF2942
1.1.9.2.4   Create new task to ZF7942

1.1.9.2.10  Select by device to be provisioned
1.1.9.2.11  By schedule provisioning configuration task
            to AP and repeat test case 1.1.9.2.1-1.1.9.2.10

1.1.9.2.12  Cancel provisioning task
1.1.9.2.13  Upgrade status and result
1.1.9.2.14  Update Audit log report
1.1.9.2.15  Failed task could be restart

1.1.9.2.3   Create new task to ZF2942_hotspot
1.1.9.2.5   Create new task to ZF2741
1.1.9.2.6   Create new task to VF7811
1.1.9.2.7   Create new task to VF2825(Ruckus01)
1.1.9.2.8   Create new task to VF2825(Ruckus03)
1.1.9.2.9   Create new task to VF2825(Ruckus04)


Inputs
- model (zf2925, zf7942, zf2942,...)
- device selection for the specified model: 'group' or 'device'
  . by group: adding new group and deleting all groups are required for this
    * 3 special groups will be available: zf2925,... adding if it's not available
  . by device
- template_type
- schedule: now or schedule
  . this is an int value expressing the time in minutes
  . default: 0 (now)

Internal Variables
- timestamp: for webUI temporary variable and taskname
- taskname: select a name with model, timestamp
- aps: list of affected aps of the specified model

Expected Results
- the task on FM must be successful
- check up with the AP side: in both FM reported success and fail cases


- WebUI temp variables - naming convention:
  . _tmp_ is a dict of timestamp
  . timestamp: one script uses only one timestamp
  . var name
  ex: ap._tmp_['090102.081020']['CallHomeInterval']

NOTE:
- No need to set the call-home interval back
- Download firmware and set it back will be available on next release
  (after Manage Firmware Files testsuite is done)

TODO: Will revise this test script to make it clearer.
'''

import time
import logging
import copy
from pprint import pformat

from RuckusAutoTest.common.utils import get_timestamp, log_trace
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import create_com
from RuckusAutoTest.tests.fm.lib_FM import FailMessages, wait4_ap_up, \
        get_ap_default_cli_cfg, wait4_ap_stable, set_ap_factory
from RuckusAutoTest.components import Helpers as lib


class FM_CfgUpgrade(Test):
    required_components=['FM', 'APs']
    parameter_description = {
        'model': 'the AP model: zf2925, zf7942, zf2942,... (default: zf2925)',
        'device_select_by': 'group/device (default: device)',
        'template_type': '...',
        'schedule': 'Now/Time in Mins (default: 0 - Now)',
        'options': 'list of configurations',
    }


    def config(self, conf):
        self.errmsg = ''

        self.aliases = self._init_aliases()

        self._cfgTestParams(**conf)
        self._calculateExecTime()


    def test(self):
        self._createCfgTemplate()
        if self.errmsg != '': return ('FAIL', self.errmsg)

        if self.steps['executeUpgrade']:
            self.steps['executeUpgrade']()

        if self.errmsg != '': return ('FAIL', self.errmsg)

        if self.steps['followUpTask']:
            self.steps['followUpTask']()

        if self.errmsg !='': return ('FAIL', self.errmsg)

        self.steps['testTheResults']()

        if self.errmsg !='': return ('FAIL', self.errmsg)

        return ('PASS', '')


    def cleanup(self):
        '''
        - For each AP:
          . Removing all the temp variables
          . ...
        '''
        try:
            a = self.aliases
            self.errmsg = ''

            if self.steps['restoreAp']:
                    self.steps['restoreAp']()
            if self.errmsg != '':
                logging.info('Cannot restore the default config')

            if self.p:
                self._deleteChangeCfgTemplate()
                if self.errmsg != '': logging.info(self.errmsg)

            a.fm.logout()
            # delete all variable of the test
            del self.aliases, self.p, self.aps, self.timestamp
        except Exception, e:
            logging.debug('Fail to cleaning the test script: %s' % str(e))
            log_trace()


    def _deleteChangeCfgTemplate(self):
        '''
        This function to delete the cfg template which was used to provision to APs
        '''
        # print '---------------Start: _deleteChangeCfgTemplate----------------'
        a = self.aliases
        self.errmsg = ''
        try:
            if self.p.has_key('template'):
                a.fm.delete_cfg_template_by_name(self.p['template'])
            else:
                logging.info('No configuration template created for the test')
        except Exception:
            self.errmsg = 'Cannot delete the configuration template %s' % self.p['template']

        # print '---------------Finish: _deleteChangeCfgTemplate----------------'


    def _init_aliases(self):
        class Aliases:
            tb  = self.testbed
            fm, aps  = tb.components['FM'], tb.components['APs']
            sfm, lfm, cfm = fm.selenium, fm.resource['Locators'], fm.resource['Constants']
        return Aliases()


    def _cfgTestParams(self, **kwa):
        self.p = {
            'model':            'zf2925',
            'device_select_by': 'device',
            'schedule':         0,
            'options': {},
        }
        self.p.update(kwa)
        self._cfgSteps(test_type=self.p['test_type'])

        logging.info('Start to test for test type "%s"' % self.p['test_type'])

        self.timestamp = get_timestamp()
        self.p['taskname'] = '%s_%s' % (self.p['model'], self.timestamp)

        self.aps = None
        self._getAndInitAffectedAps(**self.p)
        # if provision to a device, add "ip" param to select the device by ip.
        if self.p['device_select_by'] == 'device': self.p['ip'] = self.aps[0].ip_addr

        if self.steps['updateTestParams']: self.steps['updateTestParams']()
        logging.debug('Test Configs:\n%s' % pformat(self.p))


    def _getAndInitAffectedAps(self, **kwa):
        '''
        - For each AP:
          . Set the call home interval on AP side to minimum (and get that interval)
          . Get current AP firmware
          . Store these info to APs as temp attrs
        kwa:
        - model
        '''
        a = self.aliases
        self.aps = a.tb.getApByModel(kwa['model'])

        logging.info('Get and init all affected Aps (model=%s)' % kwa['model'])
        if len(self.aps) == 0: raise Exception(FailMessages['NoApFoundWithInputModel'] % kwa['model'])

        # check whether ap resource free before starting ap web ui
        if self.steps['initAp']:
            self._wait4_ap_stable()
            self.steps['initAp']()


    def _createNewAPsIfHasNewUserAndPassword(self):
        a = self.aliases
        new_aps = None
        # if the options has 'device_general' key and this key has username, password keys.
        # We need to update username, passowd of APs before doing the test
        if self.p['options'].has_key('device_general') and \
            (self.p['options']['device_general'].has_key('username') or \
            self.p['options']['device_general'].has_key('username')):
            new_aps = []
            for ap in self.aps:
                new_conf = copy.deepcopy(ap.config)
                new_conf['username'] = self.p['options']['device_general']['username'] \
                                        if self.p['options']['device_general'].has_key('username') else ap.config['username']

                new_conf['password'] = self.p['options']['device_general']['password'] \
                                        if self.p['options']['device_general'].has_key('password') else ap.config['password']

                new_ap = create_com(self.p['model'], new_conf, a.tb.selenium_mgr)
                new_ap.init_temp_storage(timestamp=self.timestamp)
                new_aps.append(new_ap)

        return new_aps


    def _waitForAPReadyToTest(self):
        '''
        This function will check if provision some configuration items which
        require AP rebooted. In this case it will sleep a moment to wait for
        AP ready to use again.
        Note: Current we only have some items which take time to provision.
            1. 'wmode', 'country_code': take time to reboot
            2. 'downlink', 'uplink': Rate Limiting takes time to apply.

            If there are more items, we will add more
        '''
        logging.info('---------------Start: _waitForAPReadyToTest---------------')
        #a = self.aliases
        #time_to_sleep = 10
        k = 'wlan_common' #a.cfm['PRO_WLAN_COMMON_TITLE']
        item1 = 'wmode'
        item2 = 'country_code'

        logging.info('Wait for AP ready to test')

        # the idea is that let _wait4_ap_stable get username/password from ap instance
        # if the username/password hasn't been changed
        change_username, change_password = None, None
        # If user changed user and password, need to assign new username and password to AP
        if self.provisioned_cfg_options.has_key('device_general'):
            if self.provisioned_cfg_options['device_general'].has_key('username'):
                change_username = self.provisioned_cfg_options['device_general']['username']
            if self.provisioned_cfg_options['device_general'].has_key('password'):
                change_password = self.provisioned_cfg_options['device_general']['password']

        if self.provisioned_cfg_options.has_key(k) and \
           (self.provisioned_cfg_options[k].has_key(item1) or\
           self.provisioned_cfg_options[k].has_key(item2)):
            # sleep to wait for the first AP enter into reboot progress.
            logging.info('Sleeping a moment to wait for AP to enter reboot status')
            time.sleep(30)

            # Next, wait for all APs boot up
            for ap in self.aps:
                config = get_ap_default_cli_cfg()
                ap_config = ap.get_cfg()
                config['ip_addr'] = ap_config['ip_addr']
                config['username'] = ap_config['username'] if not change_username else change_username
                config['password'] = ap_config['password'] if not change_password else change_password
                if not wait4_ap_up(**{'config': config, 'timeout': 6}):
                    self.errmsg += 'Cannot login to AP via cli %s after 6 mins waiting' \
                                    % (config['ip_addr'])

        self._wait4_ap_stable(username=change_username, password=change_password)
        logging.info('---------------Start: _waitForAPReadyToTest---------------')


    def _wait4_ap_stable(self, **kwa):
        '''
        This function is to check CPU usage of AP and wait for each ready to test.
        Note: if provide username password, this function will use that username/password
        instead of username/password from ap instance to connect to AP and monitor its CPU usage.
        kwa:
        - username: username to log in test APs
        - password: password to log in test APs
        '''
        _kwa = {
            'username': None,
            'password': None,
        }
        _kwa.update(kwa)

        # monitor AP CPU usage to wait for its load < 40% after rebooting or provisioning
        MONITOR_CPU_USAGE = 0
        ap_cli_config = get_ap_default_cli_cfg()

        monitor_cpu_cfg= {
            #'config': config,
            'monitor': MONITOR_CPU_USAGE,
            'threshold': 40, # default % CPU Usage
            'timeout': 20, # in minute
            'interval': 2,
            'times_to_check': 3,
        }
        for ap in self.aps:
            tb_cfg = ap.get_cfg()

            ap_cli_config['ip_addr'] = tb_cfg['ip_addr']
            ap_cli_config['username'] = _kwa['username'] if _kwa['username'] else tb_cfg['username']
            ap_cli_config['password'] = _kwa['password'] if _kwa['password'] else tb_cfg['password']

            monitor_cpu_cfg.update({'config': ap_cli_config})
            msg = 'The CPU of AP %s looks free for the test' % ap_cli_config['ip_addr']\
                    if wait4_ap_stable(**monitor_cpu_cfg) else \
                    ('WARNING: The CPU usage of AP %s is still too high' % ap_cli_config['ip_addr'])
            logging.info(msg)


    def _calculateExecTime(self, **kwa):
        '''
        - Calculate the total execution time, timeout
          . exec time of each device
          . total 'timeout'
        '''
        # TODO: move these to a more general place (likes utils or lib_FM)
        #       these should be based on the real AP model intervals
        self.ApLoadCfg = 1 # mins
        self.ApCfgTimeOut = 14 # mins
        self.FmTries = 2 # times
        self.timeout = (self.ApCfgTimeOut + \
                        self.ApLoadCfg + self.p['schedule']) * self.FmTries

        # Set timeout to test failed test case. Currently time for FM update a task failed
        # about 18 minutes so we need to make sure timeout greater than 18
        TIME_FAILED_TASK = 40
        if self.p['test_type'].lower() == 'status' and self.timeout < TIME_FAILED_TASK:
            self.timeout += TIME_FAILED_TASK - self.timeout

        logging.debug('Total task timeout: %s' % self.timeout)


    def _createCfgTemplate(self):
        # based on template_type, creating the template, named it
        logging.info('--------------Start: _createCfgTemplate---------------')
        self.errmsg = ''
        a = self.aliases
        # Variable contains list of cfg options user want to upgrade

        self.p['template'] = 'Cfg_Upgrade_' + self.p['model'] +'_' + self.timestamp

        try:
            self.provisioned_cfg_options = self.p['options']

            fm_cfg_template = {
                'template_name': self.p['template'],
                'template_model': self.p['model'].upper(),#map_template_model,
                'options': self.provisioned_cfg_options,
                'convert_in_advanced': True,
            }

            a.fm.create_cfg_template(**fm_cfg_template)
            logging.info('Created a new configuration template %s for the test successfully' % self.p['template'])
        except Exception, e:
            self.errmsg = 'Failed to create a new template %s for the test. Error: %s' % \
                          (self.p['template'], str(e))
            log_trace()

        logging.info('--------------Finish: _createCfgTemplate---------------')


    def _cfg_cfg_upgrade(self):
        a = self.aliases
        self.errmsg = ''
        logging.info('Configure a Config Upgrade for model %s' % self.p['model'])
        delta = 0
        try:
            delta = a.fm.cfg_cfg_upgrade(**self.p)
        except Exception, e:
            if e.__str__() == 'Group "%s" not found' % self.p['model']:
                logging.debug('Not found the group %s. Create a new group for this model' % self.p['model'])
                a.fm.create_model_group(**self.p)
                time.sleep(3)
                delta = a.fm.cfg_cfg_upgrade(**self.p)
            else:
                log_trace()
                raise Exception(e.__str__())

        self.timeout += delta # update the timeout


    def _createdCfgUpgradeForUpdateLogTest(self):
        '''
        This task is to create a list of task then
        '''
        #log_test_cfg = []
        pass


    def _monitor_cfg_upgrade_task(self):
        a, self.errmsg = self.aliases, ''
        logging.info('Monitor Config Upgrade task "%s" for model %s' % \
                      (self.p['taskname'], self.p['model']))
        _kwa = {'timeout': self.timeout}
        _kwa.update(self.p)
        # monitor the task on FM WebUi, total timeout is given here
        try:
            self.task_status, self.task_details = a.fm.monitor_cfg_upgrade_task(**_kwa)
            logging.info('Task Status: %s and Details:\n%s' % \
                          (self.task_status, self.task_details))
        except Exception, e:
            self.errmsg = e.__str__()
            logging.info(self.errmsg)


    def _testAPCfgs(self):
        logging.info('--------------Start: _testAPCfgs--------------')

        if len(self.task_status) != 1 or self.task_status[0][1].lower() != 'success':
                self.errmsg = 'Fail to upgrade configuration for test APs. Current status: %s' %\
                              self.task_status[0][1].lower()
                return

        self._waitForAPReadyToTest()

        logging.info('Test the AP Provisioned Config for model %s' % self.p['model'])
        self.errmsg = ''
        new_aps = self._createNewAPsIfHasNewUserAndPassword()
        tested_aps = new_aps if new_aps != None else self.aps

        # Remove un-neccessary items in wlan detail before doing compare before FM and AP config
        # In the future will add better code to remove all nesscessa
        logging.info('Add/Remove items before doing compare')
        fm_cfg_options = self._add_removeSomeItemsForComparison(**self.provisioned_cfg_options)

        for ap in tested_aps:
            logging.info('Testing for AP with config: %s' % ap.config)

            try:
                ap_map_func = {
                    'device_general': ap.get_device_items,
                    'wlan_common': ap.get_wlan_common_items,
                    'wlan_1': ap.get_wlan_det_items,
                    'wlan_2': ap.get_wlan_det_items,
                    'wlan_3': ap.get_wlan_det_items,
                    'wlan_4': ap.get_wlan_det_items,
                    'wlan_5': ap.get_wlan_det_items,
                    'wlan_6': ap.get_wlan_det_items,
                    'wlan_7': ap.get_wlan_det_items,
                    'wlan_8': ap.get_wlan_det_items,
                }

                ap.start(15)
                #tmp = ap._tmp_[self.timestamp]
                for k,v in fm_cfg_options.iteritems():
                    if v != None:
                        ap_info = ap_map_func[k](**v) # Base on items of v to get those info from ap
                        msg = self._compareTwoDicts(**{'FM':v, 'AP':ap_info})
                        if msg != '' :
                            self.errmsg += k + ': ' + msg + '\n'
                        del ap_info
                    # after access a page to get information, sleep a little time
                    time.sleep(5)

            except Exception, e:
                self.errmsg += str(e)
                log_trace()
            ap.stop()

        logging.info('--------------Finish: _testAPCfgs--------------')

        if self.errmsg != '':
            logging.info(self.errmsg)
            return
        else:
            logging.info('All APs are upgraded successully')


    def _compareTwoDicts(self, **kwargs):
        '''
        This function is to compare values of two dictionaries. Note, two dictionaries
        has the same keys.
        '''
        items = {
            'FM':"",
            'AP':"",
        }
        items.update(kwargs)
        logging.info('FM infor: %s' % pformat(items['FM']))
        logging.info('AP infor: %s' % pformat(items['AP']))
        msg = ''
        for k in items['FM'].iterkeys():
            if items['FM'][k].lower() != items['AP'][k].lower():
                msg += 'Error: Item "%s" has difference: (FM, AP): (%s,%s)\n' % (k, items['FM'][k],items['AP'][k])
                #return False

        return msg


    def _add_removeSomeItemsForComparison(self, **kwargs):
        '''
        This function is to remove unnecessary items of WLAN detail before doing
        the comparison with info got from AP.
        Input:
        - kwargs is the list of WLAN Det parameters
        '''
        removed_items = ['client_isolation', 'client_isolation', 'rate_limiting', 'cwep_pass',
                        'cpsk_passphrase', 'cauth_secret', 'cacct_secret']

        options = {}
        options.update(kwargs)

        # Remove unnecessary forr wlan 1 to 8
        for i in range(1,9):
            k = 'wlan_%d' % i # a.cfm['PRO_WLAN_%d_TITLE' % i]
            if options.has_key(k):
                # It causes errors if we change size of the dictionary while iter its keys
                temp = {}
                temp.update(options[k])
                # Add necessary items first
                if temp.has_key('rate_limiting') and temp['rate_limiting'].lower() == 'disabled':
                    # Add uplink/donwlink key for commparison
                    # Zero is value of uplink/downlink when Rate Limiting is DISABLED
                    temp['downlink'], temp['uplink'] = '0', '0'

                # Then remove unused items for comparison
                for item in options[k].iterkeys():
                    if item in removed_items:
                        temp.pop(item)

                options[k] = temp

        removed_items = ['username', 'password', 'cpassword']
        k = 'device_general' # a.cfm['PRO_DEV_GENERAL_TITLE']
        if options.has_key(k):
            temp = {}
            temp.update(options[k])
            for item in options[k].iterkeys():
                if item in removed_items:
                    temp.pop(item)

            options[k] = temp

        return options


    def _cfgSteps(self, **kwa):
        '''
        kwa:
        - test_type: this will be used to define function
        '''
        self.steps = {
            'normal': {
                # step for init config()
                'updateTestParams': None, # _cfgTestParam
                # steps for test()
                'initAp': self._set_ap_mgmt_to_auto,#None,
                'executeUpgrade': self._cfg_cfg_upgrade,
                'followUpTask': self._monitor_cfg_upgrade_task,
                'testTheResults': self._testAPCfgs,
                # steps for cleanup()
                'restoreAp': self._restore_default_ap_config,
            },
            'cancel': {
                # steps for config()
                'updateTestParams': self._updateTestParamsCancelCase, # _cfgTestParam
                # steps for test()
                'initAp': None,
                'executeUpgrade': self._cfg_cfg_upgrade,
                'followUpTask': self._cancel_cfg_upgrade_task,
                'testTheResults': self._testStatusCancelledCfgUpgradeTask,
                # steps for cleanup()
                'restoreAp': None,
            },
            'status': {
                # steps for config()
                'updateTestParams': self._updateTestParamsFailedCase,
                # steps for test()
                'initAp': self._set_ap_mgmt_to_snmp,
                'executeUpgrade': self._cfg_cfg_upgrade,
                'followUpTask': self._monitor_cfg_upgrade_task,
                'testTheResults': self._testStatusFailedFmUpgradeTask,
                # steps for cleanup()
                'restoreAp': self._set_ap_mgmt_to_auto,
            },
            'update_log':{
                # steps for config()
                'updateTestParams': None,
                # steps for test()
                'initAp': None,
                'executeUpgrade': None,
                'followUpTask': None,
                'testTheResults': self._testUpdateAuditLog,
                # steps for cleanup()
                'restoreAp': None,
            }
        }[kwa['test_type']]


    def _updateTestParamsCancelCase(self):
        params = {
            'device_select_by': 'device',
            'schedule': 13,
        }
        self.p.update(params)

    def _updateTestParamsFailedCase(self):
        params = {
            'device_select_by': 'device',
            'schedule': 0,
        }
        self.p.update(params)


    def _testStatusCancelledCfgUpgradeTask(self):
        '''
        - Make sure the status is 'cancelled'
        - Go to Audit log and make sure it is 'canceled'
        - Audit Type for Task cancelled: "Task Canceled"
        '''
        if not self.task_status[0][1].lower() in ['canceled', 'cancelled']:
            self.errmsg = 'Failed to cancelled task... tbd'
            return


    def _testStatusFailedFmUpgradeTask(self):
        '''
        - Make sure the task is failed
        - The total wait time will be printed out for later references
        NOTE: From 8.1.0.0.3, the task status only shows "expired" for fail cases.
              Don't know how to make it report "failed"
        '''
        if self.task_status[0][1].lower() == 'expired': return

        self.errmsg = 'It is expected the task fail but it is reports as %s' % self.task_status[0][1]


    def _testUpdateAuditLogForCancelledTask(self):
        '''
        Make sure Audit Log update for the Task Cancelled
        '''
        self.errmsg = ''
        _kwa = {'audit_type': 'task cancel', 'message': self.p['taskname']}
        a = self.aliases
        self.errmsg = ''
        try:
            r = a.fm.get_audit_log_item(**_kwa)
            if r:
                # successfully cancelled task here!
                logging.debug('Found the canceled task: %s' % r['Message'])
                return
            self.errmsg = 'Cancelled task is not in Audit Log... tbd'
        except Exception, e:
            self.errmsg = str(e)
            log_trace()

        if self.errmsg: logging.info(self.errmsg)


    def _testUpdateAuditLogForFailedTask(self):
        '''
        Make sure Audit Log update for the Task Failed
        NOTE: As confirm from Allen, the Audit Log doesn't update log for Failed and Success cases.
        '''
        _kwa = {'audit_type': 'task failed', 'message': self.p['taskname']}

        # TODO: Currently, FM doesn't update Audit Log for "Task Failed" case,
        #       so temporarily we will always return fail for this case.
        self.errmsg = ''
        r = None
        # r = a.fm.get_audit_log_item(**_kwa)
        if r == None:
            self.errmsg = 'Failed task is not in Audit Log... tbd'
        # successfully cancelled task here!
        #logging.debug('Found the failed task: %s' % r['Message'])


    def _testUpdateAuditLogForCreatedTask(self):
        '''
        Make sure Audit Log update for the Task Cancelled
        '''
        a = self.aliases
        self.errmsg = ''
        try:
            # Get task id of the taskname
            task_id = a.fm.get_task_id(taskname=self.p['taskname'])

            _kwa = {'audit_type': 'Configuration upgraded', 'message': 'id %s' % task_id}
            r = a.fm.get_audit_log_item(**_kwa)
            if r == None:
                self.errmsg = 'Created task is not in Audit Log... tbd'
            # successfully cancelled task here!
            logging.debug('Found the Created task: %s' % r['Message'])
        except Exception, e:
            self.errmsg = str(e)
            log_trace()


    def _testUpdateAuditLogForSuccessTask(self):
        '''
        Make sure Audit Log update for the Task Success
        NOTE: As confirm from Allen, the Audit Log doesn't update log for Failed and Success cases.
        '''

        _kwa = {'audit_type': 'task success', 'message': self.p['taskname']}

        # TODO: Currently, FM doesn't update Audit Log for "Task Success" case,
        #       so temporarily we will always return fail for this case.
        self.errmsg = ''
        r = None
        # r = a.fm.get_audit_log_item(**_kwa)
        if r == None:
            self.errmsg = 'Success task is not in Audit Log... tbd'
        # successfully cancelled task here!
        #logging.debug('Found the success task: %s' % r['Message'])


    def _testUpdateAuditLog(self):
        '''
        Make sure the Audit Log update status for Created, Failed, Cancelled task.
        # TODO: Currently, FM doesn't have log record for Success/Failed Task, so
                we only verify Update Audit Log for Created/Canceled cases.

        Note: This is a special function so it has a little difference from other cases
        '''
        logging.info('-----------Start: _testUpdateAuditLog-------------')
        self.errmsg = ''

        # Create a scheduled task to test Update Audit Log for Created/Cancelled task
        #old_name = self.p['taskname']
        self.p['taskname'] = 'Cancel_' + self.p['taskname']
        self.p['schedule'] = 13
        self._cfg_cfg_upgrade()

        tmp = ''
        logging.info('Testing Update Audit Log for Created Task')
        self._testUpdateAuditLogForCreatedTask()

        if self.errmsg != '':
            tmp += self.errmsg + '\n'

        logging.info('Testing Update Audit Log for Cancel Task')
        self._cancel_cfg_upgrade_task()
        self._testUpdateAuditLogForCancelledTask()

        if self.errmsg != '':
            tmp += self.errmsg + '\n'

        self.errmsg = tmp
        logging.info('-----------Finish: _testUpdateAuditLog-------------')


    def _cancel_cfg_upgrade_task(self):
        a = self.aliases
        self.errmsg = ''
        logging.info('Cancel Configuration Upgrade task "%s" for model %s' % \
                      (self.p['taskname'], self.p['model']))
        _kwa = {'timeout': self.timeout}
        _kwa.update(self.p)
        # cancel the task on FM WebUi, total timeout is given here
        try:
            self.task_status, self.task_details = a.fm.cancel_cfg_upgrade_task(**_kwa)
            logging.debug('Task Status: %s and Details:\n%s' % \
                          (self.task_status, pformat(self.task_details)))
        except Exception, e:
            self.errmsg = e.__str__()


    def _setApFmUrl(self):
        '''
        '''
        a = self.aliases
        new_aps = self._createNewAPsIfHasNewUserAndPassword()
        test_aps = new_aps if new_aps != None else self.aps
        fm_url = "http://%s/intune/server" % a.fm.get_cfg()['ip_addr']

        for ap in test_aps:
            ap.start(5)
            try:
                ap.set_fm_url(url=fm_url, validate_url=False)
            except Exception:
                log_trace()
                logging.info('Warning: Cannot set FM url of AP %s to %s' %
                             (ap.get_cfg()['ip_addr'], fm_url))
            ap.stop()


    def _set_ap_mgmt_to_snmp(self):
        '''
        For cleaning up on Failed case
        '''
        logging.info('Set management type of all test APs to Snmp')
        for ap in self.aps:
            ap.start(15)
            ap.set_mgmt_type(**{'type': 'snmp'})
            ap.stop()


    def _set_ap_mgmt_to_auto(self):
        '''
        For cleaning up on Failed case
        '''
        logging.info('Set management type of all test APs to Auto')
        for ap in self.aps:
            ap.start(15)
            ap.set_mgmt_type(**{'type': 'auto'})
            ap.stop()

    def _restore_default_ap_config(self):
        '''
        Restore default config for tested aps
        '''
        a, select_cfg = self.aliases, {}
        restore_tmpl_name = "Restore_" + self.p['template']
        restore_taskname  = "Restore_" + self.p['taskname']

        logging.info('Restore default config...')
        lib.fm.cfg_tmpl.create_cfg_tmpl_2(
            a.fm, restore_tmpl_name, self.p['model'].upper(), self.p['restore_cfg']
        )
        if self.p['device_select_by'] == 'device':
            select_cfg['device'] = self.aps[0].ip_addr
        else:
            select_cfg['group'] = self.p['model']

        ts, detail = lib.fm.cfg_upgr.create_task(
            a.fm, restore_taskname, restore_tmpl_name, self.p['model'].upper(),
            0, select_cfg
        )
        if not a.fm.lib.cfg_upgr.is_success_status(ts):
            logging.info(
                'Warning: Cannot restore default config. Status: %s. Detail: %s' %
                (ts, detail)
            )

        a.fm.lib.cfg_tmpl.delete_cfg_tmpl(a.fm, restore_tmpl_name)

