'''
Testsuite
1.1.9.5. Factory Reset Testsuite
normal
  1.1.9.5.1 Create new Factory Reset task select by group
  1.1.9.5.2 Create new Factory Reset task select by device
  1.1.9.5.3 By schedule and repeat test cases 1.1.9.5.1-1.1.9.5.2
cancel
  1.1.9.5.4 Cancel the Reset task
result
  1.1.9.5.5 Result of Factory Reset task
FM 8.x
  1.1.9.5.6 Failed task could be restart

Note:
- How to know the AP has been factory reset?
  By provisioning something (likes Device Name) and make sure it is
  reset to default after factory reset.
'''

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.fm.lib_FM import *


class FM_FactoryReset(Test):
    required_components=['FM', 'APs']
    parameter_description = {
        'test_type': 'the type of test: normal, cancel, result',
        'model': 'the AP model: zf2925, zf7942, zf2942,... (default: zf2925)',
        'device_select_by': 'group/device (default: device)',
        'reboot': 'True/False (default: True)',
        'schedule': 'Now/Time in Mins (default: 0 - Now)',
    }


    def config(self, conf):
        self.errmsg = None
        self._cfgTestParams(**conf)
        self._calculateExecIntervals()
        self._cfgAps() # provision config to AP for testing


    def test(self):
        self._cfgFactoryReset()
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
            'reboot':           True,
            'schedule':         0,
            'device_name':      ['ruckus01', 'ruckus02'],
        }
        self.p.update(kwa)
        self.aliases = init_aliases(testbed=self.testbed)
        self._cfgSteps(test_type=self.p['test_type'])

        self.timestamp = get_timestamp()
        self.p['device_name'] = ['%s_%s' % (self.timestamp, dn) for dn in self.p['device_name']]
        self.p['taskname'] = '%s_%s' % (self.p['model'], self.timestamp)

        self.aps = self._getAndInitAffectedAps(**self.p)

        if self.steps['updateTestParams']: self.steps['updateTestParams']()
        logging.debug('Test Configs:\n%s' % pformat(self.p))


    def _updateTestParamsCancelCase(self):
        params = {
            'device_select_by': 'device',
            'reboot': True,
            'schedule': 30,
        }
        self.p.update(params)


    def _updateTestParamsOtherCases(self):
        params = {
            'device_select_by': 'device',
            'reboot': True,
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
                'followUpTask': self._monitorFactoryResetTask,
                'testTheResults': self._testAPCfg,
                'updateTestParams': None,
                'initAp': None,
                'restoreAp': None,
            },
            'cancel': {
                'followUpTask': self._cancelFactoryResetTask,
                'testTheResults': self._testCancelledFactoryResetTask,
                'updateTestParams': self._updateTestParamsCancelCase,
                'initAp': None,
                'restoreAp': None,
            },
            'result': {
                'followUpTask': self._monitorFactoryResetTask,
                'testTheResults': self._testFailedFactoryResetTask,
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
            # remove set AP call home interval time
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
        self.ApFactoryResetTimeOut = 2 # mins
        self.ApRebootTimeOut = 5 # mins
        self.FmTries = 3 # times
        self.timeout = ((self.ApRebootTimeOut if self.p['reboot'] else 0) + \
                        self.ApFactoryResetTimeOut + self.p['schedule'] + \
                        self.FmWaitTime) * self.FmTries

        # expecting the time format: 1 hr 2 mins 16 secs
        # this is the map between AP displayed and datetime.timedelta format
        self.DateTimeSeps = {'day':'days', 'hr':'hours',
                             'min':'minutes', 'sec':'seconds'}
        self.ProvTimeStamp = None # recorded provisioned timestamp
        # TODO: remove the hack here
        if self.p['test_type'] == 'result':
            self.timeout += 15 # more mins for waiting
        logging.debug('Total task timeout: %s' % self.timeout)


    def _cfgAps(self):
        '''
        for the list of affected APs
        - go to device view and change the AP name to something else
        - go to cli and remove the persistence data
        '''
        a = self.aliases
        for ap in self.aps:
            # using one in 2 given names
            sel_name = self.p['device_name'][0]
            dv = a.fm.get_device_view(ip=ap.ip_addr)
            if sel_name.strip().lower() == dv.get_device_name().strip().lower():
                sel_name = self.p['device_name'][1]
            logging.info('Config Device Name - "%s" - from Device View for AP %s' %
                         (sel_name, ap.ip_addr))
            dv.set_device_name(sel_name)
            a.fm.cleanup_device_view(dv)

            ap_conf = {'ip_addr': ap.ip_addr, 'telnet': True, 'port': 23}
            clear_persistent_cfg(config=ap_conf)


    def _cfgFactoryReset(self):
        a = self.aliases
        logging.info('Configure a FactoryReset for model %s' % self.p['model'])
        delta = 0
        try:
            delta = lib.fm.factoryReset.cfg(a.fm, **self.p)
        except Exception, e:
            if e.__str__() == 'Group "%s" not found' % self.p['model']:
                a.fm.create_model_group(**self.p)
                delta = lib.fm.factoryReset.cfg(a.fm, **self.p)
            else:
                raise Exception(e)
        self.timeout += delta # update the timeout
        self.ProvTimeStamp = datetime.datetime.now() # recording the provisioned timestamp


    def _monitorFactoryResetTask(self):
        a = self.aliases
        logging.info('Monitor FactoryReset task "%s" for model %s' % \
                     (self.p['taskname'], self.p['model']))
        _kwa = {'timeout': self.timeout}
        _kwa.update(self.p)
        # monitor the task on FM WebUi, total timeout is given here
        self.task_status, self.task_details = lib.fm.factoryReset.monitor_task(a.fm, **_kwa)
        logging.debug('Task Status: %s and Details:\n%s' % \
                      (self.task_status, pformat(self.task_details)))


    def _testAPCfg(self):
        logging.info('Test the AP Up time for model %s' % self.p['model'])
        allowed_delta = datetime.datetime.now() - self.ProvTimeStamp # max allowed time
        logging.debug('Provisioned time delta: %s' % allowed_delta)
        start_waiting_delta = datetime.datetime.now()
        for ap in self.aps:
            ap_cli = None
            config = {'ip_addr': ap.ip_addr, 'telnet': True, 'port': 23}
            logging.debug('Ap cli config: %s' % str(config))
            if not self.p['reboot']:
                if not reboot_ap(config):
                    self.errmsg = 'Reboot too long (AP %s)' % ap.ip_addr
                    return
            else:
                # Wait for the ap to be up before testing it
                if not wait4_ap_up(config=config, timeout=self.ApRebootTimeOut):
                    self.errmsg = 'Reboot too long (AP %s)' % ap.ip_addr
                    return

            ap.start()
            ap_name = ap.get_device_status()['Device Name'].strip()
            logging.debug('AP Device Name: %s; Preconfig names: %s' %
                          (ap_name, ', '.join(self.p['device_name'])))

            if ap_name.strip() in self.p['device_name']:
                self.errmsg = FailMessages['ApFailedToFactoryReset'] % \
                    (ap.ip_addr, ap_name, self.task_status)
                ap.stop()
                return
            ap.stop()

        # success! all aps are upgraded, check back the reported task status
        if len(self.task_status) == 1 and self.task_status[0][1].lower() == 'success': return
        self.errmsg = FailMessages['ApFactoryResetedFmReportsFail']


    def _cancelFactoryResetTask(self):
        a = self.aliases
        logging.info('Cancel FactoryReset task "%s" for model %s' % \
                      (self.p['taskname'], self.p['model']))
        _kwa = {'timeout': self.timeout}
        _kwa.update(self.p)
        # cancel the task on FM WebUi, total timeout is given here
        try:
            self.task_status, self.task_details = lib.fm.factoryReset.cancel_task(a.fm, **_kwa)
            logging.debug('Task Status: %s and Details:\n%s' % \
                          (self.task_status, pformat(self.task_details)))
        except Exception, e:
            log_trace_back()
            self.errmsg = e.__str__()


    def _testCancelledFactoryResetTask(self):
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


    def _testFailedFactoryResetTask(self):
        '''
        - Make sure the task is failed
        - The total wait time will be printed out for later references
        '''
        if len(self.task_status) == 1 and self.task_status[0][1].lower() == 'expired': return
        self.errmsg = 'It is expected the task fail but it is reports as %s' % self.task_status

