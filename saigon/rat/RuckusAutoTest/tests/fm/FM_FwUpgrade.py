'''
Testsuite
1.1.9.3. Firmware Upgrade Testsuite

normal
  1.1.9.3.1   Create fw upgrade task to ZF2925
  1.1.9.3.2   Create fw upgrade task to ZF2942(select by group)
  1.1.9.3.5   Create fw upgrade task to ZF7942(select by group)
  1.1.9.3.13  Select by device to be fw upgrade
  1.1.9.3.14  By schedule provisioning firmware task to device and repeat test case 1.1.9.3.1-1.1.9.3.13
cancel
  1.1.9.3.15  Cancel fw upgrade task
https
  1.1.9.3.16  Firmware upgrade using HTTPS
result
  1.1.9.3.17  FW Upgrade result

  1.1.9.3.3   Create fw upgrade task to ZF2942_hotspot(select by group)
  1.1.9.3.4   Create fw upgrade task to ZF2942_hotspot(select by group)
  1.1.9.3.6   Create fw upgrade task to ZF2741(select by group)
  1.1.9.3.7   Create fw upgrade task to VF7811
  1.1.9.3.8   Create fw upgrade task to VF2811
  1.1.9.3.9   Create fw upgrade task to VF2825(ruckus01)
  1.1.9.3.10  Create fw upgrade task to VF2825(ruckus03)
  1.1.9.3.11  Create fw upgrade task to VF2825(ruckus04)
  1.1.9.3.12  Create fw upgrade task to ZD(select by group)

  1.1.9.3.18  Partial successful provision result
  1.1.9.3.19  Backup image test
  1.1.9.3.20  Failed task could be restart


MODELING FOR NORMAL CASES
-------------------------
Inputs
- model (zf2925, zf7942, zf2942,...)
- device selection for the specified model: 'group' or 'device'
  . by group: adding new group and deleting all groups are required for this
    * 3 special groups will be available: zf2925,... adding if it's not available
  . by device
- firmware (for the specified model)
  . prerequisite: the firmware must be available on the server
- reboot: Yes or No (True/False)
  . default: True
  . a reboot feature on ap side is required (can be via webUI)
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


Testscript
+ Config:
  - Initialize the input config
  - Generate a unique timestamp for the script
  - Generate a task name which is unique (using script's timestamp)
  - For each AP:
    . Set the call home interval on AP side to minimum (and get that interval)
    . Get current AP firmware
    . Store these info to APs as temp attrs
  - Calculate the total execution time, timeout

+ Test:
  - Configuring the web UI
    . Navigate to Prov> Firmware Upgrade page
    . Create new Firmware Upgrade task
    . Select devices by group or devices. Output is a list of devices (same model)
      . If a specific group is not found then raise an Exception
      . The testscript (caller) is responsible for catch and handle this exception:
        . Create new group
        . Restart the config task
      . If there is 'Not-Registered' devices on the returned list, raise exception?!?
    . Set the task name
    . Select the firmware
    . Check/uncheck reboot
    . Config schedule
    . Click Save
  - Monitor the task
    . Continuously refresh the list of task and get the status: Failed, Success or timeout
    . Failed, timeout
      . Get the info from the detail list (for later debuggin')
  - Cross check AP side (in all FM reporting cases), for each AP:
    . Reboot if it is not rebooted yet
    . Get the firmware info
  - Compare these info; tbd...

+ Clean up:
  - For each AP:
    . Download the firmware on k2
    . Downgrade to previous version
    . Removing all the temp variables


BASED ON NORMAL CASE, CREATING ALTERNATIVE CASES
------------------------------------------------
1.1.9.3.15  Cancel fw upgrade task
Inputs
- model
- firmware

Internal Variables
- device selection by 'device'
- reboot: Yes(True)
- schedule: an acceptable value
------
- timestamp: for webUI temporary variable and taskname
- taskname: select a name with model, timestamp
- aps: list of affected aps of the specified model


Testscript
+ Config:
  - Set the schedule param to an acceptable value
+ Test:
  - Cancel the task (instead of monitor it)
  - Test it differently by another test function
    . make sure the task status is cancelled
    . and audit log reports the cancelled task
+ Cleanup:
  - Don't change the ap firmware



1.1.9.3.16  Firmware upgrade using HTTPS
Inputs
- model
- firmware

Internal Variables
- device selection by 'device'
- reboot: Yes (True)
- schedule: 0 (Now)
------
- nothing changes

Testscript
+ Config:
  - Set the 'FlexMaster Server URL' on for each AP to use https
+ Test:
  - Just likes normal case
+ Cleanup:
  - Since the AP will be downgraded, no need to change 'FM URL' back


1.1.9.3.17  FW Upgrade result
Inputs
- model
- firmware

Internal Variables
- device selection by 'device'
- reboot: Yes (True)
- schedule: 0 (Now)
------
- nothing changes

Testscript
  Just test the fail case, the pass case is covered on 1.1.9.3.1
+ Config:
  - For each AP, change management to 'SNMP only'
+ Test:
  - Test func:
    . Make sure the task is fail
+ Cleanup:
  - Change the management back to 'Auto'


NOTE:
- No need to set the call-home interval back
- Download firmware and set it back will be available on next release
  (after Manage Firmware Files testsuite is done)
'''

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.tests.fm.lib_FM import *

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib


class FM_FwUpgrade(Test):
    required_components=['FM', 'APs']
    parameter_description = {
        'test_type': 'the type of test: normal, cancel, https, result',
        'model': 'the AP model: zf2925, zf7942, zf2942,... (default: zf2925)',
        'device_select_by': 'group/device (default: device)',
        'firmware': 'the upgraded firmware',
        'reboot': 'True/False (default: True)',
        'schedule': 'Now/Time in Mins (default: 0 - Now)',
    }


    def config(self, conf):
        self.errmsg = None
        self._cfgTestParams(**conf)
        self._calculateExecIntervals()
        self._uploadFwsIfNotExist()


    def test(self):
        self._cfgFwUpgrade()
        if self.errmsg: return ('FAIL', self.errmsg)

        # step 2: either monitor or cancel the task
        self.steps['followUpTask']()
        if self.errmsg: return ('FAIL', self.errmsg)

        # step 3: test differently for normal and https; cancel; result
        self.steps['testTheResults']()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', '')


    def cleanup(self):
        '''
        - For each AP:
          . Download the firmware on k2
          . Downgrade to previous version
          . Removing all the temp variables
        '''
        a = self.aliases
        # @note: to fix "FM_FwUpgrade instance has no attribute 'aps'" issue
        try:
            self.aps
        except:
            self.aps = []
        for ap in self.aps:
            ap.start()
            if self.steps['restoreAp']: self.steps['restoreAp'](ap=ap)
            ap.stop()
            ap._tmp_.pop(self.timestamp)
        if self.steps['downgradeFw']: self.steps['downgradeFw']()
        a.fm.logout()


    def _cfgTestParams(self, **kwa):
        self.p = {
            'test_type':        'normal',
            'model':            'zf2925',
            'device_select_by': 'device',
            'firmware':         '7.1.0.0.37.Bl7',
            'downgradeFw':      '7.1.0.0.37.Bl7',
            'reboot':           True,
            'schedule':         0,
        }
        self.p.update(kwa)
        self.aliases = init_aliases(testbed=self.testbed)

        self._cfgSteps(test_type=self.p['test_type'])

        self.timestamp = get_timestamp()
        self.p['taskname'] = '%s_%s' % (self.p['model'], self.timestamp)

        self.firmware = self._initFirmware(firmware=self.p['firmware'])
        self.orgFws = ['%s_%s' % (self.p['model'][2:], self.p['firmware']),
                       '%s_%s' % (self.p['model'][2:], self.p['downgradeFw'])]
        self.p['firmware'] = '*%s*' % self.p['firmware']
        self.p['downgradeFw'] = '*%s*' % self.p['downgradeFw']

        self.aps = self._getAndInitAffectedAps(**self.p)

        if self.steps['updateTestParams']: self.steps['updateTestParams']()
        logging.debug('Test Configs:\n%s\n' % pformat(self.p))


    def _initFirmware(self, **kwa):
        '''
        keep a backup for comparing
        kwa:
        - firmware
        '''
        fw = kwa['firmware'].split('.Bl')[0]
        if '_FCS' in fw:
            fw = fw.split('_FCS')[0]
        return fw


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
                'followUpTask': self._monitorFwUpgradeTask,
                'testTheResults': self._testAPFirmwares,
                'updateTestParams': None,
                'initAp': None,
                'restoreAp': None,
                'downgradeFw': self._downgradeFw,
            },
            'cancel': {
                'followUpTask': self._cancelFwUpgradeTask,
                'testTheResults': self._testCancelledFwUpgradeTask,
                'updateTestParams': self._updateTestParamsCancelCase,
                'initAp': None,
                'restoreAp': None,
                'downgradeFw': None,
            },
            'https' : {
                'followUpTask': self._monitorFwUpgradeTask,
                'testTheResults': self._testAPFirmwares,
                'updateTestParams': self._updateTestParamsOtherCases,
                'initAp': self._setApFmUrlUsingHttps,
                'restoreAp': self._setApFmUrlUsingHttp,
                'downgradeFw': self._downgradeFw,
            },
            'result': {
                'followUpTask': self._monitorFwUpgradeTask,
                'testTheResults': self._testFailedFmUpgradeTask,
                'updateTestParams': self._updateTestParamsOtherCases,
                'initAp': set_ap_mgmt_to_snmp,
                'restoreAp': set_ap_mgmt_to_auto,
                'downgradeFw': None,
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
            tmp = ap.init_temp_storage(timestamp=self.timestamp)
            tmp['firmware'] = ap.get_device_status()['Software Version']
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
        self.ApLoadFw = 4 # mins
        self.ApRebootTimeOut = 4 # mins
        self.FmTries = 3 # times
        self.timeout = ((self.ApRebootTimeOut if self.p['reboot'] else 0) + \
                        self.ApLoadFw + self.p['schedule'] + \
                        self.FmWaitTime) * self.FmTries
        logging.debug('Total task timeout: %s' % self.timeout)


    def _cfgFwUpgrade(self):
        a = self.aliases
        logging.info('Configure a Firmware Upgrade for model %s' % self.p['model'])
        delta = 0
        try:
            delta = lib.fm.fwUpgrade.cfg(a.fm, **self.p)
        except Exception, e:
            if e.__str__() == 'Group "%s" not found' % self.p['model']:
                logging.info('The specific group "%s" is not found. Create it' % self.p['model'])
                a.fm.create_model_group(**self.p)
                delta = lib.fm.fwUpgrade.cfg(a.fm, **self.p)
            else:
                raise

        self.timeout += delta # update the timeout
        logging.debug('Total wait time after added schedule delta: %s' % self.timeout)


    def _monitorFwUpgradeTask(self):
        a = self.aliases
        logging.info('Monitor Firmware Upgrade task "%s" for model %s' % \
                      (self.p['taskname'], self.p['model']))
        _kwa = {'timeout': self.timeout}
        _kwa.update(self.p)
        # monitor the task on FM WebUi, total timeout is given here
        self.task_status, self.task_details = lib.fm.fwUpgrade.monitor_task(a.fm, **_kwa)
        logging.debug('Task Status: %s and Details:\n%s' % \
                       (self.task_status, pformat(self.task_details)))


    def _downgradeFw(self):
        param = dict(
            firmware= self.p['downgradeFw'],
            schedule= 0,
            reboot=   True,
        )
        self.p.update(param)
        self._cfgFwUpgrade()
        self._monitorFwUpgradeTask()


    def _testAPFirmwares(self):
        logging.info('Test the AP Firmware version for model %s' % self.p['model'])
        for ap in self.aps:
            # creating an AP Cli instance, ask it to reboot
            # the wait time might be different for each AP model!!!
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
            tmp = ap._tmp_[self.timestamp]
            ap_firmware = ap.get_device_status()['Software Version']

            if self.firmware != ap_firmware:
                self.errmsg = FailMessages['FirmwareMismatch'] % \
                    (ap.ip_addr, ap_firmware, self.firmware, self.task_status)
                ap.stop()
                return

            ap.stop()

        # success! all aps are upgraded, check back the reported task status
        if len(self.task_status) == 1 and self.task_status[0][1].lower() == 'success': return
        self.errmsg = FailMessages['ApUpgradedFmReportsFail']


    def _cancelFwUpgradeTask(self):
        a = self.aliases
        logging.info('Cancel Firmware Upgrade task "%s" for model %s' % \
                      (self.p['taskname'], self.p['model']))
        _kwa = {'timeout': self.timeout}
        _kwa.update(self.p)
        # cancel the task on FM WebUi, total timeout is given here
        try:
            self.task_status, self.task_details = lib.fm.fwUpgrade.cancel_task(a.fm, **_kwa)
            logging.debug('Task Status: %s and Details:\n%s' % \
                          (self.task_status, pformat(self.task_details)))
        except Exception, e:
            log_trace_back()
            self.errmsg = e.__str__()


    def _testCancelledFwUpgradeTask(self):
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


    def _setApFmUrlUsingHttps(self, **kwa):
        '''
        For testing HTTPS case, this function is called on the loop of
        _getAndInitAffectedAps()
        - On AP side, configure the FM URL to use HTTPS
        - Refresh a couple times make sure it is really HTTPS
        kwa:
        - ap
        '''
        a = self.aliases
        _kwa = { 'url': 'https://%s/intune/server' % a.fm.ip_addr }
        _kwa.update(kwa)
        _kwa['ap'].set_fm_url(url=_kwa['url'])


    def _setApFmUrlUsingHttp(self, **kwa):
        '''
        For testing HTTPS case, this function is called on the loop of
        _getAndInitAffectedAps()
        - On AP side, configure the FM URL to use HTTPS
        - Refresh a couple times make sure it is really HTTPS
        kwa:
        - ap
        '''
        a = self.aliases
        _kwa = { 'url': 'http://%s/intune/server' % a.fm.ip_addr }
        _kwa.update(kwa)
        _kwa['ap'].set_fm_url(url=_kwa['url'])


    def _testFailedFmUpgradeTask(self):
        '''
        - Make sure the task is failed
        - The total wait time will be printed out for later references
        '''
        if len(self.task_status) == 1 and self.task_status[0][1].lower() == 'expired': return
        self.errmsg = 'It is expected the task fail but it is reports as %s' % self.task_status


    def _uploadFwsIfNotExist(self):
        logging.info('Upload testing firmwares if not exist')
        fmFws = [fw['firmwarename'] for fw in lib.fm.fw.get_all_firmwares(self.aliases.fm)]
        for fw in self.orgFws:
            if fw not in fmFws:
                lib.fm.fw.upload_firmware(self.aliases.fm, models=[self.p['model']],
                                       filepath=os.path.join(init_firmware_path(), fw))
