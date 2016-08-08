'''
Testsuite
1.1.9.4 Reboot

normal
  1.1.9.4.1 Create new reboot task select by AP group
  1.1.9.4.2 Create new reboot task select by device
  1.1.9.4.4 By schedule and repeat test cases 1.1.9.4.1-1.1.9.4.3
cancel
  1.1.9.4.5 Cancel the reboot task
result
  1.1.9.4.6 Result of reboot task
FM 8.x
  1.1.9.4.3 Create new reboot task select by ZD group
  1.1.9.4.7 Failed task could be restart


MODELING FOR NORMAL CASES
-------------------------
Inputs
- model (zf2925, zf7942, zf2942,...)
- device selection for the specified model: 'group' or 'device'
  . by group: adding new group and deleting all groups are required for this
    * 3 special groups will be available: zf2925,... adding if it's not available
  . by device
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


Testscript
+ Config:
  - Initialize the input config
  - Generate a unique timestamp for the script
  - Generate a task name which is unique (using script's timestamp)
  - For each AP:
    . Set the call home interval on AP side to minimum (and get that interval)
  - Calculate the total execution time, timeout

+ Test:
  - Configuring the web UI
    . Navigate to Prov> Reboot page
    . Create new task
    . Select devices by group or devices. Output is a list of devices (same model)
      . If a specific group is not found then raise an Exception
      . The testscript (caller) is responsible for catch and handle this exception:
        . Create new group
        . Restart the config task
      . If there is 'Not-Registered' devices on the returned list, raise exception?!?
    . Set the task name
    . Config schedule
    . Click Save
  - Monitor the task
    . Continuously refresh the list of task and get the status: Failed, Success or timeout
    . Failed, timeout
      . Get the info from the detail list (for later debuggin')
  - Cross check AP side (in all FM reporting cases)
  - Compare these info; tbd...

+ Clean up:
  - For each AP:
    . Removing all the temp variables (if any)

'''
import logging
import datetime
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common.utils import get_timestamp, log_trace
from RuckusAutoTest.tests.fm.lib_FM import init_aliases, set_ap_mgmt_to_snmp, \
        set_ap_mgmt_to_auto, FailMessages, wait4_ap_up, \
        convert_str_to_time_delta


class FM_ApReboot(Test):
    required_components=['FM', 'APs']
    parameter_description = {
        'test_type': 'the type of test: normal, cancel, https, result',
        'model': 'the AP model: zf2925, zf7942, zf2942,... (default: zf2925)',
        'device_select_by': 'group/device (default: device)',
        'schedule': 'Now/Time in Mins (default: 0 - Now)',
    }


    def config(self, conf):
        self.errmsg = None
        self._cfgTestParams(**conf)
        self._calculateExecIntervals()


    def test(self):
        self._cfgReboot()
        if self.errmsg: return ('FAIL', self.errmsg)

        # step 2: either monitor or cancel the task
        self.steps['followUpTask']()
        if self.errmsg: return ('FAIL', self.errmsg)

        # step 3: test differently for normal; cancel; result cases
        self.steps['testTheResults']()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', '')


    def cleanup(self):
        '''
        - For each AP:
          . Restoring some configs
          . Removing all the temp variables
        '''
        a = self.aliases
        for ap in self.aps:
            if self.steps['restoreAp']:
                ap.start()
                self.steps['restoreAp'](ap=ap)
                ap.stop()
        a.fm.logout()


    def _cfgTestParams(self, **kwa):
        self.p = {
            'test_type':        'normal',
            'model':            'zf2925',
            'device_select_by': 'device',
            'schedule':         0,
        }
        self.p.update(kwa)
        self.aliases = init_aliases(testbed=self.testbed)
        self._cfgSteps(test_type=self.p['test_type'])

        self.timestamp = get_timestamp()
        self.p['taskname'] = '%s_%s' % (self.p['model'], self.timestamp)

        self.aps = self._getAndInitAffectedAps(**self.p)

        if self.steps['updateTestParams']: self.steps['updateTestParams']()
        logging.debug('Test Configs:\n%s' % pformat(self.p))


    def _updateTestParamsCancelCase(self):
        params = {
            'device_select_by': 'device',
            'schedule': 30,
        }
        self.p.update(params)


    def _updateTestParamsOtherCases(self):
        params = {
            'device_select_by': 'device',
            'schedule': 0,
        }
        self.p.update(params)


    def _cfgSteps(self, **kwa):
        '''
        kwa:
        - test_type: this will be used to define function
        '''
        self.steps = {
            'normal': {
                'followUpTask': self._monitorRebootTask,
                'testTheResults': self._testAPUpTime,
                'updateTestParams': None,
                'initAp': None,
                'restoreAp': None,
            },
            'cancel': {
                'followUpTask': self._cancelRebootTask,
                'testTheResults': self._testCancelledRebootTask,
                'updateTestParams': self._updateTestParamsCancelCase,
                'initAp': None,
                'restoreAp': None,
            },
            'result': {
                'followUpTask': self._monitorRebootTask,
                'testTheResults': self._testFailedRebootTask,
                'updateTestParams': self._updateTestParamsOtherCases,
                'initAp': set_ap_mgmt_to_snmp,
                'restoreAp': set_ap_mgmt_to_auto,
            },
        }[kwa['test_type']]


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
        logging.info('Get and init all affected Aps (model=%s)' % kwa['model'])
        aps = a.tb.getApByModel(kwa['model'])
        if len(aps) == 0: raise Exception(FailMessages['NoApFoundWithInputModel'] % kwa['model'])

        for ap in aps:
            ap.start()
            # remove set call home interval time
            if self.steps['initAp']: self.steps['initAp'](ap=ap)
            ap.stop()
            
        return aps


    def _calculateExecIntervals(self, **kwa):
        '''
        - Calculate the total execution time, timeout
          . exec time of each device
          . total 'timeout'
        '''
        # TODO: move these to a more general place (likes utils or lib_FM)
        #       these should be based on the real AP model intervals
        self.FmWaitTime = 15 # mins ( for each AP)
        self.ApRebootTimeOut = 5 # mins
        self.FmTries = 3 # times
        self.timeout = (self.ApRebootTimeOut + self.p['schedule'] + \
                        self.FmWaitTime) * self.FmTries

        # expecting the time format: 1 hr 2 mins 16 secs
        # this is the map between AP displayed and datetime.timedelta format
        self.DateTimeSeps = {'day':'days', 'hr':'hours',
                             'min':'minutes', 'sec':'seconds'}
        self.ProvTimeStamp = None # recorded provisioned timestamp
        # TODO: remove the hack here
        if self.p['test_type'] == 'result':
            self.timeout += 10 # more mins for waiting
            if self.p['model'] == 'zf2942':
                self.timeout += 15
        logging.debug('Total task timeout: %s' % self.timeout)


    def _cfgReboot(self):
        a = self.aliases
        logging.info('Configure a Reboot for model %s' % self.p['model'])
        delta = 0
        try:
            delta = lib.fm.apReboot.cfg(a.fm, **self.p)
        except Exception, e:
            if e.__str__() == 'Group "%s" not found' % self.p['model']:
                a.fm.create_model_group(**self.p)
                delta = lib.fm.apReboot.cfg(a.fm, **self.p)
            else:
                raise Exception(e)
        self.timeout += delta # update the timeout
        self.ProvTimeStamp = datetime.datetime.now() # recording the provisioned timestamp


    def _monitorRebootTask(self):
        a = self.aliases
        logging.info('Monitor Reboot task "%s" for model %s' % \
                     (self.p['taskname'], self.p['model']))
        _kwa = {'timeout': self.timeout}
        _kwa.update(self.p)
        # monitor the task on FM WebUi, total timeout is given here
        self.task_status, self.task_details = lib.fm.apReboot.monitor_task(a.fm, **_kwa)
        logging.debug('Task Status: %s and Details:\n%s' % \
                      (self.task_status, pformat(self.task_details)))


    def _testAPUpTime(self):
        logging.info('Test the AP Up time for model %s' % self.p['model'])
        allowed_delta = datetime.datetime.now() - self.ProvTimeStamp # max allowed time
        logging.debug('Provisioned time delta: %s' % allowed_delta)
        start_waiting_delta = datetime.datetime.now()
        for ap in self.aps:
            ap_cli = None
            config = {'ip_addr': ap.ip_addr, 'telnet': True, 'port': 23}
            logging.debug('Ap cli config: %s' % str(config))
            # Wait for the ap to be up before testing it
            if not wait4_ap_up(config=config, timeout=self.ApRebootTimeOut):
                self.errmsg = 'Reboot too long (AP %s)' % ap.ip_addr
                return
            # Calculate the boot up wait delta
            allowed_delta = allowed_delta + (datetime.datetime.now() - start_waiting_delta)
            ap.start()
            ap_uptime = ap.get_device_status()['Uptime'].strip()
            uptime = convert_str_to_time_delta(str=ap_uptime, seperators=self.DateTimeSeps)
            logging.debug('Allowed Time Delta: %s; AP Uptime: %s; Converted AP Uptime: %s' % \
                          (allowed_delta, ap_uptime, uptime))

            if uptime >= allowed_delta:
                self.errmsg = FailMessages['ApFailedToReboot'] % \
                    (ap.ip_addr, ap_uptime, self.task_status)
                ap.stop()
                return
            ap.stop()

        # success! all aps are upgraded, check back the reported task status
        if len(self.task_status) == 1 and self.task_status[0][1].lower() == 'success': return
        self.errmsg = FailMessages['ApRebootedFmReportsFail']


    def _cancelRebootTask(self):
        a = self.aliases
        logging.info('Cancel Reboot task "%s" for model %s' % \
                      (self.p['taskname'], self.p['model']))
        _kwa = {'timeout': self.timeout}
        _kwa.update(self.p)
        # cancel the task on FM WebUi, total timeout is given here
        try:
            self.task_status, self.task_details = lib.fm.apReboot.cancel_task(a.fm, **_kwa)
            logging.debug('Task Status: %s and Details:\n%s' % \
                          (self.task_status, pformat(self.task_details)))
        except Exception, e:
            log_trace()
            self.errmsg = e.__str__()


    def _testCancelledRebootTask(self):
        '''
        - Make sure the status is 'cancelled'
        - Go to Audit log and make sure it is 'canceled'
        '''
        a = self.aliases
        if not (len(self.task_status) == 1 and self.task_status[0][1].lower() == 'canceled'):
            self.errmsg = 'Failed to cancelled task... tbd'
            return

        _kwa = {'audit_type': 'task cancel', 'message': self.p['taskname']}
        r = a.fm.get_audit_log_item(**_kwa)
        if r == None:
            self.errmsg = 'Cancelled task is not in Audit Log... tbd'
        # successfully cancelled task here!
        logging.debug('Found the canceled task: %s' % r['Message'])


    def _testFailedRebootTask(self):
        '''
        - Make sure the task is failed
        - The total wait time will be printed out for later references
        '''
        if len(self.task_status) == 1 and self.task_status[0][1].lower() == 'expired': return
        self.errmsg = 'It is expected the task fail but it is reports as %s' % self.task_status

