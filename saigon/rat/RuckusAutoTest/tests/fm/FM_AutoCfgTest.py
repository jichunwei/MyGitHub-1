'''
Testsuite
1.1.7.3.1    Device group select "All Standalone Aps"
1.1.7.3.1.1    Auto configuration test for ZF2942(AP6.0/AP7.0/AP8.0)
1.1.7.3.1.2    Auto configuration test for ZF2925(AP6.0/AP7.0/AP8.0)
1.1.7.3.1.3    Auto configuration test for ZF7942(AP7.0/AP8.0)
1.1.7.3.1.4    Auto configuration test for VF2825
1.1.7.3.1.5    Auto configuration test for VF7811
1.1.7.3.1.6    Auto configuration test for VF2741
1.1.7.3.1.7    Pre-registeration data test by Tag name
1.1.7.3.1.8    Auto configuration priority check
1.1.7.3.1.9    Already registrer AP test
1.1.7.3.1.10    Create a device group base on "Serial number" then Device group select this one  and repeat test case 1.1.7.3.1.1-1.1.7.3.1.6


Inputs

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


I. Procedure for tcs: This one is "normal" test
1.1.7.3.1.1    Auto configuration test for ZF2942(AP6.0/AP7.0/AP8.0)
1.1.7.3.1.2    Auto configuration test for ZF2925(AP6.0/AP7.0/AP8.0)
1.1.7.3.1.3    Auto configuration test for ZF7942(AP7.0/AP8.0)
1.1.7.3.1.4    Auto configuration test for VF2825
1.1.7.3.1.5    Auto configuration test for VF7811
1.1.7.3.1.6    Auto configuration test for VF2741

1. Create a configuration template for a specific model
2. Create an auto configuration rule with using following items:
    + Device Group: "All Standalone APs"
    + Model type: model which used to create the template and that model
    + Configuration template: the config templated created
3. Change AP serial and set factory it to make it as a new AP registered to FM
4. Go to Inventory > Device Registration > Registration Status and make sure that device marked as "Auto Configured"
5. Go to AP WebUI and make AP configured as the template.

II. Procedure for tc: This one is "pre-Registration" test
1.1.7.3.1.7    Pre-registeration data test by Tag name

1. Create an Excel data file for pre-registration with two columns: first column for serial, the second for Tag Name
2. Upload that file to FM
3. Change AP serial to serial created in the data file and set factory the AP to make it as a new AP registered to FM
4. Go to Inventory > Device Registration > Registration Status and make sure that device has Auto Configured Tag
   as you created in the data file
5. Go to Inventory > Manage Device > Saved Groups and make sure that device has Tag Name as you created in the data file

III. Procedure for tc: This one is "priorityCheck" test
1.1.7.3.1.8    Auto configuration priority check

The same as 1.1.7.3.1.1 "I" but we create two auto configuration rule and make sure the first rule applied to AP
not the second rule

IV. Procedure for tc: This one is "pre-Registration" test
1.1.7.3.1.9    Already registrer AP test

1. Create a configuration template for a specific model
2. Create an auto configuration rule with using following items:
    + Device Group: "All Standalone APs"
    + Model type: model which used to create the template and that model
    + Configuration template: the config templated created
3. Make sure that the rule doesn't auto configure APs which already registered to FM

V. Procedure for tcs: This one is "serialBase" test
1.1.7.3.1.10.1    Create a ZF2925 device group base on "Serial number" then Device group select this one  and do auto configuration test
1.1.7.3.1.10.2    Create a ZF2942 device group base on "Serial number" then Device group select this one  and do auto configuration test
1.1.7.3.1.10.3    Create a ZF7942 device group base on "Serial number" then Device group select this one  and do auto configuration test

1. Create a configuration template for a specific model
2. Create a new device group base on "serial".
2. Create an auto configuration rule with using following items:
    + Device Group: Select "Device Group" which has just been created
    + Model type: model which used to create the template and that model
    + Configuration template: the config templated created
3. Change AP serial and set factory it to make it as a new AP registered to FM
4. Go to Inventory > Device Registration > Registration Status and make sure that device marked as "Auto Configured"
5. Go to AP WebUI and make AP configured as the template.

Internal variables:
    1. p: dictionary which following keys:
       - model: model to do the test,
       - test_type: following test test: normal, registeredAp, priorityCheck, serialBase, and pre-Registration
       - device_group: 'All Standalone APs', 'serial group'
       - 'options': a dictionary contains configuration for "normal, registeredAp, priorityCheck,
                    and serialBase" test. It looks like
                    {
                        'device_general': {....},
                        'wlan_common': {},
                        ....
                    }
        - auto_cfg_rule: rule name

    2. test_aps: a list of AP and each element is a dictionary with following keys
       - ap_webui: object of AP WebUI
       - ip_addr: ip address of this AP
       - ori_serial: keep the real serial of AP to restore later
       - new_serial: a new serial change it to this serial to do the test
       - tag: Tag Name for this AP (this one is used for pre-Registration test)

    3. timestamp: get timestamp for each running the test and use it in the name of auto config rule, config template
       to make it unique.

Steps to do for each type of test: refer to _cfgSteps function for more detail
    1. 'normal':
        - 'initTest': self._initNormalTest,
        - 'executeMainJob': self._doNormalTest,
        - 'followUpTask': self._monitor_device_registration,
        - 'testTheResults': self._doVerifyAutoCfgForNormalTest,
        - 'restoreCfg': self._doRestoreForNormalTest,

    2. 'registeredAp':
        - 'initTest': self._initRegisteredApTest,
        - 'executeMainJob': self._doRegisteredApTest,
        - 'followUpTask': None,
        - 'testTheResults': self._doVerifyAutoCfgForRegisteredAp,
        - 'restoreCfg': self._doRestoreForRegisteredApTest,

    3. 'priorityCheck':
        - 'initTest': self._initNormalTest,
        - 'executeMainJob': self._doNormalTest,
        - 'followUpTask': self._monitor_device_registration,
        - 'testTheResults': self._doVerifyAutoCfgForNormalTest,
        - 'restoreCfg': self._doRestoreForNormalTest,

    4. 'serialBase':
    # This test is the same normal test
        - 'initTest': self._initNormalTest,
        - 'executeMainJob': self._doNormalTest,
        - 'followUpTask': self._monitor_device_registration,
        - 'testTheResults': self._doVerifyAutoCfgForNormalTest,
        - 'restoreCfg': self._doRestoreForNormalTest,

     5. 'pre-Registration':
        - 'initTest': self._initPreRegTest,
        - 'executeMainJob': self._doPreRegTest,
        - 'followUpTask': self._monitor_device_registration,
        - 'testTheResults': self._doVerifyAutoCfgForPreRegTest,
        - 'restoreCfg': self._doRestoreForNormalTest,

'''

import os
import time
import logging
import traceback
import copy
from pprint import pformat

from RuckusAutoTest.common.utils import log_trace
from RuckusAutoTest.common.utils import get_timestamp, try_times, log_trace
from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.fm.lib_FM import FailMessages, get_ap_serial, reboot_ap, \
        wait4_ap_up, set_ap_serial, set_ap_factory, \
        get_ap_default_cli_cfg, wait4_ap_stable
from RuckusAutoTest.components.lib.ap import access as acc_lib
from RuckusAutoTest.components import Helpers as lib

class FM_AutoCfgTest(Test):
    required_components=['FM', 'APs']
    parameter_description = {
        'model': 'Required. the AP model: zf2925, zf7942, zf2942,... (default: zf2925)',
        'options':'Required. List of configuration options to do Auto Configure',
    }


    def config(self, conf):
        self.errmsg = ''

        self.aliases = self._init_aliases()

        self._cfgTestParams(**conf)
        self._calculateExecTime()
        self._initCommonErrMsg()


    def test(self):

        if self.steps['initTest']: self.steps['initTest']()
        if self.errmsg != '': return ('FAIL', self.errmsg)

        if self.steps['executeMainJob']: self.steps['executeMainJob']()
        if self.errmsg != '': return ('FAIL', self.errmsg)

        if self.steps['followUpTask']: self.steps['followUpTask']()
        if self.errmsg != '': return ('FAIL', self.errmsg)

        self.steps['testTheResults']()
        if self.errmsg !='': return ('FAIL', self.errmsg)

        return ('PASS', '')


    def cleanup(self):
        '''
        - For each AP:
          . Restore its original serial
          . ...
        '''
        try:
            a = self.aliases
            self.errmsg = ''

            if self.steps['restoreCfg']: self.steps['restoreCfg']()
            if self.errmsg != '':
                logging.info('Cannot restore the default config. Error: %s' % self.errmsg)

            a.fm.logout()
        except Exception:
            logging.debug('Some error happend while cleaning the test script %s' % traceback.format_exc())


    def _init_aliases(self):
        class Aliases:
            tb  = self.testbed
            fm, aps  = tb.components['FM'], tb.components['APs']
            sfm, lfm, cfm = fm.selenium, fm.resource['Locators'], fm.resource['Constants']
        return Aliases()


    def _initCommonErrMsg(self):
        '''
        This function is to define error messages used in some different function
        '''
        # Define error message for the compare two dictionary function "_compareTwoDicts" (it is used to compare
        # AP and FM config).
        # Be carefull if you changed this message!!! It may affect to _verifyAutoCfgForRegisteredAP,
        # this function uses this message for its result
        self.COMPARISON_PHRASE = 'has difference: (FM, AP)'
        self.DIFF_CFG_MSG = 'Error: Item "%s" ' +  self.COMPARISON_PHRASE + ' (%s,%s)\n'


    def _cfgTestParams(self, **kwa):
        self.p = {
            'model': 'zf2925',
            'test_type': 'normal',
            'device_group': 'All Standalone APs',
            'options': {},
            'tag': '', # this para is only used for preg-Registration test
            'cpu_threshold': 10,
        }
        self.p.update(kwa)
        self.p['model'] = self.p['model'].upper()

        logging.info('Init for the test "%s"' % self.p['test_type'])
        self._cfgSteps(test_type=self.p['test_type'])

        self.timestamp = get_timestamp()

        self.test_aps = self._getAndInitAffectedAps(**self.p)

        # No need auto config rule for "pre-Registration" test
        if self.p['test_type'] != 'pre-Registration':
            self._create_auto_cfg_ruleName()

        #if self.steps['updateTestParams']: self.steps['updateTestParams']()
        logging.debug('Test Configs:\n%s' % pformat(self.p))


    def _create_auto_cfg_ruleName(self):
        '''
        This function is base on test_type to create auto config rule for the test
        '''
        self.p['cfg_rule_name'] = 'Auto_Cfg_%s_%s' % (self.p['model'], self.timestamp)

        if self.p['test_type'] == 'priorityCheck':
            self.p['ex_cfg_rule_name'] = 'Ex_Auto_Cfg_%s_%s' % (self.p['model'], self.timestamp)

        elif self.p['test_type'] == 'serialBase':
            self.p['cfg_rule_name'] = []
            for i in range(len(self.test_aps)):
                rule = 'Auto_Cfg_%s_%s_%02d' % (self.p['model'], self.timestamp, i+1)
                self.p['cfg_rule_name'].append(rule)


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
        ap_cfg = {
            'ap_webui': None,
            'ip_addr': '',
            'ori_serial': '',
            'new_serial': '',
        }

        logging.info('Get and init all affected Aps (model=%s)' % kwa['model'])
        aps = a.tb.getApByModel(kwa['model'])
        if len(aps) == 0: raise Exception(FailMessages['NoApFoundWithInputModel'] % kwa['model'])

        test_aps = []
        for ap in aps:
            tmp_cfg = copy.deepcopy(ap_cfg)
            config= {
                'ip_addr': ap.config['ip_addr']
            }
            tmp_cfg = {
                'ap_webui': ap,
                'ip_addr': ap.config['ip_addr'],
                'ori_serial': get_ap_serial(**{'config':config}),
                'new_serial': '',
            }

            test_aps.append(tmp_cfg)

        return test_aps


    def _calculateExecTime(self, **kwa):
        '''
        - Calculate the total execution time, timeout
          . exec time of each device
          . total 'timeout'
        '''
        # TODO: move these to a more general place (likes utils or lib_FM)
        #       these should be based on the real AP model intervals
        self.ApLoadCfg = 3 # mins
        self.ApCfgTimeOut = 10 # mins
        self.FmTries = 3 # times
        self.timeout = (self.ApCfgTimeOut + \
                        self.ApLoadCfg) * self.FmTries
        # Time out for default config
        #self.timeout2 = self.timeout

        # Set timeout to test failed test case. Currently time for FM update a task failed
        # about 18 minutes so we need to make sure timeout greater than 18
        #TIME_FAILED_TASK = 20
        #if self.p['test_type'].lower() == 'status' and self.timeout < TIME_FAILED_TASK:
        #    self.timeout += TIME_FAILED_TASK - self.timeout

        logging.debug('Total task timeout: %s' % self.timeout)


    def _createCfgTemplate(self):
        # based on template_type, creating the template, named it
        logging.info('--------------Start: _createCfgTemplate---------------')
        self.errmsg = ''
        a = self.aliases

        try:
            self.p['cfg_template_name'] = 'Auto_Cfg_' + self.p['model'] +'_' + self.timestamp
            fm_cfg_template = {
                'template_name': self.p['cfg_template_name'],
                'template_model': self.p['model'].upper(), # map_template_model,
                'options': self.p['options'], #self.provisioned_cfg_options
                'convert_in_advanced': True,
            }
            a.fm.create_cfg_template(**fm_cfg_template)
            logging.info('Created a new configuration template %s for the test successfully' % self.p['cfg_template_name'])

            if self.p['test_type'].lower() == 'prioritycheck':
                # Create another template for this test
                self.p['ex_cfg_template_name'] = 'Ex_Auto_Cfg_' + self.p['model'] +'_' + self.timestamp
                fm_cfg_template = {
                    'template_name': self.p['ex_cfg_template_name'],
                    'template_model': self.p['model'].upper(), # map_template_model,
                    'options': self.p['ex_options'], #self.provisioned_cfg_options
                    'convert_in_advanced': True,
                }
                a.fm.create_cfg_template(**fm_cfg_template)

        except Exception:
            self.errmsg = 'Failed to create a template %s for the test. Error: %s' % \
                          (fm_cfg_template['template_name'], traceback.format_exc())
            logging.debug(self.errmsg)

        logging.info('--------------Finish: _createCfgTemplate---------------')


    def _generateNewSerialsForStressTest(self):
        '''
        Base on number of APs to create new serials respectively
        '''
        logging.info('--------------Start: _generateNewSerials---------------')
        self.errmsg = ''
        a = self.aliases

        no_ap = self.p['no_rule']
        try:
            serials = a.fm.generate_unique_ap_serials(**{'no': no_ap, 'prefix': 'ZF'})
            for i in range(no_ap):
                self.test_aps[i]['new_serial'] = serials[i]

            logging.info('List of AP infomation: %s' % self.test_aps)
        except Exception, e:
            self.errmsg = 'Cannot generate new serials for the test. Error: %s' % e.__str__()
            log_trace()
            logging.info(self.errmsg)

        logging.info('--------------Finish: _generateNewSerials---------------')


    def _generateNewSerials(self):
        '''
        Base on number of APs to create new serials respectively
        '''
        logging.info('--------------Start: _generateNewSerials---------------')
        self.errmsg = ''
        a = self.aliases

        no_ap = len(self.test_aps)
        try:
            serials = a.fm.generate_unique_ap_serials(**{'no': no_ap, 'prefix': 'ZF'})
            for i in range(no_ap):
                self.test_aps[i]['new_serial'] = serials[i]

            logging.info('List of APs infomation: %s' % self.test_aps)
        except Exception, e:
            self.errmsg = 'Cannot generate new serials for the test. Error: %s' % e.__str__()
            logging.info(self.errmsg)

        logging.info('--------------Finish: _generateNewSerials---------------')


    def _initNormalTest(self):
        '''
        To init test for tcs:
        1.1.7.3.1.1    Auto configuration test for ZF2942(AP6.0/AP7.0/AP8.0)
        1.1.7.3.1.2    Auto configuration test for ZF2925(AP6.0/AP7.0/AP8.0)
        1.1.7.3.1.3    Auto configuration test for ZF7942(AP7.0/AP8.0)

        - cfg_rule_name
        - device_group: group of devices to aplly this rule
        - model: model to apply this rule
        - cfg_template_name: The template for this rule
        '''
        logging.info('--------------Start: _initNormalTest---------------')
        a = self.aliases
        self.errmsg = ''
        logging.info('Creating a new config template for the test...')
        # Create a new configuration template
        self._createCfgTemplate()
        if self.errmsg != '': return

        logging.info('Generating new unique AP serials for the test...')
        # Create new serial for a list of tested APs
        self._generateNewSerials()
        if self.errmsg != '': return

        if self.p['test_type'] == 'serialBase':
            # Create a group base new serial
            # For this test: If our system has a few of APs 2925 or 2942 or 7942, we will create each group for each AP.
            # Ex: we have two ZF2925s, => Create two groups base on their serials for each 2925.
            self._createDeviceGroup()
            #self._create_auto_cfg_ruleList()

        logging.info('Test device groups %s' % self.p['device_group'])


    def _initPreRegTest(self):
        '''
        This functions is to initialize for Pre-Registration test.
        Steps:
        1. Generate pre-registration data file
        2. uploade the data file to FM
        For tc: 1.1.7.3.1.7    Pre-registeration data test by Tag name
        '''
        self._generate_pre_reg_data_file()
        if self.errmsg != '': return

        self._upload_pre_reg_dataFile()
        if self.errmsg != '': return


    def _generate_pre_reg_data_file(self):
        '''
        This function is to generate a pre-registration data file in Excel format
        '''
        a = self.aliases
        self.errmsg = ''

        self.prereg_data = {
            'no': len(self.test_aps),
            'filename': 'PreRegDataFile.xls',
            'path': os.getcwd(),
            'tag': self.p['tag'],
        }

        try:
            new_aps = a.fm.generate_pre_reg_data_file(**self.prereg_data)
            # Assign new serials and new tags to test aps
            for i in range(len(self.test_aps)):
                self.test_aps[i]['new_serial'] = new_aps[i]['serial']
                self.test_aps[i]['tag'] = new_aps[i]['tag']

        except Exception:
            self.errmsg = 'Cannot create a pre-registration data file "%s" for the test' % self.prereg_data['filename']


    def _upload_pre_reg_dataFile(self):
        '''
        This function is to uploade the data file to FM
        '''
        a = self.aliases
        self.errmsg = ''

        try:
            a.fm.upload_pre_reg_data(filename=self.prereg_data['filename'], path=self.prereg_data['path'])
        except Exception, e:
            self.errmsg = 'Cannot generate pre-registration data file "%s" for the test. Error: %s' %\
                            (self.prereg_data['filename'], e.__str__())


    def _doPreRegTest(self):
        '''
        This function will do main steps
            1. Change AP serial so that AP will register to FM with new serial
            2. Wait for FM applies auto config to FM.
            3. Set FM url for each AP

        '''

        # 2. Change AP serial so that AP will register to FM with new serial
        self._changeApSerial()
        if self.errmsg !='': return

        #self._waitForAPReadyToTest()
        #if self.errmsg !='': return

        # After changeApSerial, the Ap usually uses DHCP option 43 to contact FM and the AP
        # will be configured automatically
        self._setApFmUrl()


    def _doNormalTest(self):
        '''
        This function will do main steps
            1. Create an auto config rule
            2. Change AP serial so that AP will register to FM with new serial
            3. Wait for FM applies auto config to FM.
        '''
        # Don't need to create auto configure rule for pre-Registration test
        if self.p['test_type'] != 'pre-Registration':
            # Create an auto config rule
            self._cfgAutoCfgRule()
            if self.errmsg !='': return

        # 2. Change AP serial so that AP will register to FM with new serial
        self._changeApSerial()
        if self.errmsg !='': return

        #self._waitForAPReadyToTest()
        #sif self.errmsg !='': return

        # After changeApSerial, the Ap usually uses DHCP option 43 to contact FM and the AP
        # will be configured automatically
        # after change FM url, FM takes a little time to update the change
        self._setApFmUrl()


    def _cfgAutoCfgRule(self):
        '''
        Create an auto configuration rule for this group
        '''
        a = self.aliases
        self.errmsg = ''
        logging.info('Configure an Auto Config Rule for model %s' % self.p['model'])
        delta = 0
        try:
            if self.p['test_type'] == 'serialBase':
                # The serialBase requires a few of different device groups
                for i in range(len(self.p['device_group'])):
                    cfg = {
                            'cfg_rule_name': self.p['cfg_rule_name'][i],
                            'device_group': self.p['device_group'][i],
                            'model': self.p['model'].upper(),
                            'cfg_template_name': self.p['cfg_template_name'],
                        }
                    a.fm.create_auto_cfg_rule(**cfg)
                    logging.info('Created an auto config rule "%s" for the test' % self.p['cfg_rule_name'][i])
            else:
                #Other tests: normal, registeredAp, priorityCheck
                cfg = {
                        'cfg_rule_name': self.p['cfg_rule_name'],
                        'device_group': self.p['device_group'],
                        'model': self.p['model'].upper(),
                        'cfg_template_name': self.p['cfg_template_name'],
                    }
                a.fm.create_auto_cfg_rule(**cfg)
                logging.info('Created an auto config rule "%s" for the test' % self.p['cfg_rule_name'])

                if self.p['test_type'] == 'priorityCheck':
                    # Create another template for this test
                    cfg = {
                        'cfg_rule_name': self.p['ex_cfg_rule_name'],
                        'device_group': self.p['device_group'],
                        'model': self.p['model'].upper(),
                        'cfg_template_name': self.p['ex_cfg_template_name'],
                    }
                    a.fm.create_auto_cfg_rule(**cfg)
                    logging.info('Created another auto config rule "%s" for the test' % self.p['cfg_rule_name'])

        except Exception, e:
            self.errmsg = e.__str__()


    def _changeApSerial(self):
        '''
        Change all serials of tested APs
        config of each ap:
        ap = {
            'ap_webui': None,
            'ip_addr': '',
            'ori_serial': '',
            'new_serial': '',
        }
        '''
        logging.info('-------------Start: _changeApSerial-------------')
        a = self.aliases
        self.errmsg = ''
        for ap in self.test_aps:
            config= {
                'ip_addr': ap['ip_addr']
            }
            logging.info('Change serial of AP %s to %s' % (ap['ip_addr'], ap['new_serial']))
            if not set_ap_serial(**{'serial': ap['new_serial'], 'config': config}):
                self.errmsg = 'Cannot set a new serial %s for AP %s' % (ap['new_serial'], ap['ip_addr'])
                logging.info(self.errmsg)
                return
            # logging.info('Set factory AP %s' % ap['ip_addr'] )
            # if not set_ap_factory(config=config):
            #    self.errmsg = 'Cannot set factory for AP %s after change its serial' % (ap['ip_addr'])
            #    logging.info(self.errmsg)
            #    return

            # just reboot to make new serial take effect to save time, don't need to set factory
            #logging.info('Reboot the AP %s to make new serial take effect' % ap['ip_addr'])
            if not reboot_ap(config):
                self.errmsg = 'Cannot reboot AP %s after change its serial' % (ap['ip_addr'])
                logging.info(self.errmsg)
                return

            if not wait4_ap_up(**{'config':config}):
                self.errmsg = 'The AP %s is not boot up...' % (ap['ip_addr'])
                logging.info(self.errmsg)
                return
        logging.info('-------------Finish: _changeApSerial-------------')


    def _restoreApSerial(self):
        '''
        Restore ogriginal serials for all APs
        '''
        a = self.aliases
        self.errmsg = ''
        for ap in self.test_aps:
            logging.info('Restoring original serial %s for AP %s' % (ap['ori_serial'], ap['ip_addr']))
            config= {
                'ip_addr': ap['ip_addr']
            }
            if not set_ap_serial(**{'serial': ap['ori_serial'], 'config': config}):
                self.errmsg = 'Cannot restore the original serial %s for AP %s' % (ap['ori_serial'], ap['ip_addr'])
                return

            if not set_ap_factory(config=config):
                self.errmsg = 'Cannot set factory for AP %s after restoring its original serial' % (ap['ip_addr'])
                return


    def _stopApCfgRule(self):
        '''
        To stop an auto cfg rule
        '''
        a = self.aliases
        self.errmsg = ''
        cfg_rule = ''

        if self.p['test_type'] == 'serialBase':
            for cfg_rule in self.p['cfg_rule_name']:
                try:
                    logging.info('Trying to delete the rule %s' % cfg_rule)
                    lib.fm.auto_cfg.delete_auto_cfg_rule(a.fm, cfg_rule)
                except Exception, e:
                    log_trace()
                    logging.info('Cannot delete the rule %s. Try to stop it...' % cfg_rule)
                    try:
                        a.fm.stop_auto_cfg_rule(cfg_rule_name=cfg_rule)
                    except Exception, e:
                        # cannot stop this rule, try to stop other rules.
                        logging.info(
                            'Warning: Cannot stop the rule %s. Error: %s' % (cfg_rule, e.__str__())
                        )
        else:
            try:
                cfg_rule = self.p['cfg_rule_name']
                try:
                    logging.info('Trying to delete the rule %s' % cfg_rule)
                    lib.fm.auto_cfg.delete_auto_cfg_rule(a.fm, cfg_rule)
                except:
                    log_trace()
                    logging.info('Cannot delete the rule %s. Try to stop it...' % cfg_rule)
                    a.fm.stop_auto_cfg_rule(cfg_rule_name=cfg_rule)

                if self.p['test_type'] == 'priorityCheck':
                    logging.info('Trying to stop the extra rule %s' % self.p['ex_cfg_rule_name'])
                    cfg_rule = self.p['ex_cfg_rule_name']
                    try:
                        logging.info('Trying to delete the rule %s' % self.p['cfg_rule_name'])
                        lib.fm.auto_cfg.delete_auto_cfg_rule(a.fm, cfg_rule)
                    except:
                        logging.info('Cannot delete the rule %s. Try to stop it...' % cfg_rule)
                        a.fm.stop_auto_cfg_rule(cfg_rule_name=cfg_rule)
            except Exception, e:
                self.errmsg = 'Cannot stop the rule %s. Error: %s' % (cfg_rule, e.__str__())

        logging.debug(self.errmsg)


    def _disableTestedDevicesWithNewSerial(self):
        '''
        After finish the test we need to disable tested APs with new serial
        so that they are not shown on Inventory > Manage Device
        '''
        a, self.errmsg = self.aliases, ''
        for ap in self.test_aps:
            status, serial = 'Unavailable', ap['new_serial']
            try:
                # From FM 9 it allows to remove device, try to remove new device
                # first. If it's successful, try to change it to un-available.
                if a.fm.lib.dreg.remove_device(a.fm, serial):
                    logging.info('Removed the new device %s' % serial)
            except Exception, e:
                logging.info(
                    'Cannot remove the new device %s. Change it to status %s' %
                    (serial, status)
                )
                a.fm.lib.dreg.set_device_status(
                    a.fm, serial, status, 'Automation changed to %s' % status
                )


    def _createDeviceGroup(self):
        '''
        This function is to create device group for serialBase test
        # Create a group base new serial
        # For this test: If our system has a few of APs 2925 or 2942 or 7942, we will create each group for each AP.
        # Ex: we have two ZF2925s, => Create two groups base on their serials for each 2925.
        '''
        a = self.aliases

        # BE CAREFULL: For serialBase test the variable self.p['device_group'] will be a list of device
        self.p['device_group'] = []
        for i in range(len(self.test_aps)):
            group = "Group_Serial_" + self.test_aps[i]['new_serial']
            self.p['device_group'].append(group)
            a.fm.create_serial_group(serial=self.test_aps[i]['new_serial'], name=self.p['device_group'][i])


    def _removeDeviceGroup(self):
        '''
        This function is to remove group created by serial for following tcs:
            1.1.7.3.1.10    Create a ZF2925 device group base on "Serial number" then Device group select this one  and do auto configuration test
            1.1.7.3.1.11    Create a ZF2942 device group base on "Serial number" then Device group select this one  and do auto configuration test
            1.1.7.3.1.12    Create a ZF7942 device group base on "Serial number" then Device group select this one  and do auto configuration test
        '''
        a = self.aliases
        self.errmsg = ''

        for group in self.p['device_group']:
            try:
                a.fm.remove_group(group=self.p['device_group'])
            except Exception:
                self.errmsg += 'Cannot delete device group "%s" created for the test\n' % self.p['device_group']

        if self.errmsg != '':
            logging.info(self.errmsg)


    def _doRestoreForNormalTest(self):
        '''
        This function is to do following thing:
            1. Stop auto config rule
            2. Deny AP with new serial
            3. Restore original AP serial
        '''
        err_msg = ''
        if self.p['test_type'] != 'pre-Registration':
            self._stopApCfgRule()
            if self.errmsg != '': err_msg += self.errmsg

        self._disableTestedDevicesWithNewSerial()
        if self.errmsg != '': err_msg += self.errmsg

        # The group which is configured for Auto Configuration Rule cannot be deleted
        #if self.p['test_type'] == 'serialBase':
            #self._removeDeviceGroup()
            #if self.errmsg != '': err_msg += self.errmsg

        self._restoreApSerial()
        if self.errmsg != '': err_msg += self.errmsg

        self._setApFmUrl()
        if self.errmsg != '': err_msg += self.errmsg

        self.errmsg = err_msg


    def _getDefaultCfgOptions(self):
        def_opts = {
            'device_general': {
                               'device_name': 'RuckusAP',
                               'username': 'super',
                               'password': 'sp-admin', 'cpassword': 'sp-admin'
            },

            'wlan_common': {#a dictionary, its items may be following things. Note that: it uses the title as a key
                'wmode': 'auto',
                'channel': '0', # Smart select
                'country_code': 'TW',
                'txpower': 'max',
                'prot_mode': 'Disabled'
            },
        }
        def_wlan_det = { # wlan_%{num} is "wireless num", {num} should be 1, 2, 3, 4, 5, 6, 7, 8
                'wlan_num': 'i',
                'avail': 'Disabled',
                'broadcast_ssid': 'Enabled',
                'client_isolation': 'Disabled',
                'wlan_name': 'Wirelss Name',
                'wlan_ssid': 'Wireless SSID',
                'dtim': '1',
                'frag_threshold': '2346',
                'rtscts_threshold': '2346',
                'rate_limiting': 'Disabled',
                #'downlink': '100kbps, 250kbps, 500kbps, 1mbps, 2mbps, 5mbps, 10mbps, 20mbps, 50mbps',
                #'uplink': '100kbps, 250kbps, 500kbps, 1mbps, 2mbps, 5mbps, 10mbps, 20mbps, 50mbps',
                'encrypt_method': 'Disabled',
        }
        for i in range(1,9):
            def_opts['wlan_%d' % i] = def_wlan_det.copy()
            def_opts['wlan_%d' % i]['wlan_num']  = str(i)
            def_opts['wlan_%d' % i]['wlan_name'] = 'Wireless %d' % i
            def_opts['wlan_%d' % i]['wlan_ssid'] = 'Wireless %d' % i


        if self.p['model'].lower() == 'zf7942':
            def_opts['wlan_common'].pop('wmode')

        return def_opts


    def _monitor_device_registration(self):
        a, self.errmsg = self.aliases, ''

        # monitor the task on FM WebUi, total timeout is given here
        for ap in self.test_aps:
            logging.info('Monitor device registration for model: %s, ip address: %s, serial: %s' % \
                      (self.p['model'], ap['ip_addr'], ap['new_serial']))
            _kwa = {
                'serial': ap['new_serial'],
                'timeout': self.timeout
            }
            try:
                if a.fm.monitor_device_registration(**_kwa):
                    logging.info('Found AP serial %s registered to FM' % \
                              (ap['new_serial']))
                else:
                    self.errmsg += 'Cannot find any registered AP with serial %s\n' % ap['new_serial']
                    logging.debug(self.errmsg)
            except Exception:
                #self.errmsg += e.__str__() + '\n'
                self.errmsg += traceback.format_exc() + '\n'


    def _waitForAPReadyToTest(self):
        '''
        This function is to wait AP get auto configuration from FM
        '''
        self.errmsg = ''

        cfg = self.p['options']
        k = 'wlan_common'
        item1 = 'wmode'
        item2 = 'country_code'

        change_username, change_password = None, None
        # If user changed user and password, need to assign new username and password to AP
        if cfg.has_key('device_general'):
            if cfg['device_general'].has_key('username'):
                change_username = cfg['device_general']['username']
            if cfg['device_general'].has_key('password'):
                change_password = cfg['device_general']['password']

        if cfg.has_key(k) and \
           (cfg[k].has_key(item1) or\
           cfg[k].has_key(item2)):
            # sleep to wait for the first AP enter into reboot progress.
            logging.info('Sleeping a moment to wait for AP to enter reboot status')
            time.sleep(30)

            # Next, wait for all APs boot up
            for ap in self.test_aps:
                config = get_ap_default_cli_cfg()
                ap_config = ap['ap_webui'].get_cfg()
                config['ip_addr'] = ap_config['ip_addr']
                config['username'] = ap_config['username'] if not change_username else change_username
                config['password'] = ap_config['password'] if not change_password else change_password
                if not wait4_ap_up(**{'config': config, 'timeout': 6}):
                    self.errmsg += 'Cannot login to AP via cli %s after 6 mins waiting' \
                                    % (config['ip_addr'])

        # check if AP CPU is ready for the test
        self._waitForAPResourceAvailable(username=change_username, password=change_password)


    def _waitForAPResourceAvailable(self, **kwa):
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
            'threshold': self.p['cpu_threshold'], # default % CPU Usage
            'timeout': 20, # in minute
            'interval': 2,
            'times_to_check': 3,
        }
        for ap in self.test_aps:
            tb_cfg = ap['ap_webui'].get_cfg()

            ap_cli_config['ip_addr'] = tb_cfg['ip_addr']
            ap_cli_config['username'] = _kwa['username'] if _kwa['username'] else tb_cfg['username']
            ap_cli_config['password'] = _kwa['password'] if _kwa['password'] else tb_cfg['password']

            monitor_cpu_cfg.update({'config': ap_cli_config})

            logging.info('Monitoring AP info: \n%s' % pformat(monitor_cpu_cfg))
            msg = 'The CPU of AP %s looks free for the test' % ap_cli_config['ip_addr']\
                    if wait4_ap_stable(**monitor_cpu_cfg) else \
                    'WARNING: The CPU usage of AP %s is still too high' % ap_cli_config['ip_addr']
            logging.info(msg)


    def _testFMMarksDeviceAsAutoCfg(self):
        '''
        This function is to test whether FM marks a device as "Auto Configured" with "check" symbol
        '''
        logging.info('-------------Start: _testFMMarksDeviceAsAutoCfg-------------')
        a = self.aliases
        logging.info('Test to make sure tested devices marked as Auto Configured')
        self.errmsg = ''
        for ap in self.test_aps:
            logging.info('Testing for AP ip: %s, serial: %s' % (ap['ip_addr'], ap['new_serial']))
            try:
                a.fm.is_device_auto_configured(serial=ap['new_serial'])
            except Exception, e:
                self.errmsg += e.__str__()

        logging.info('-------------Finish: _testFMMarksDeviceAsAutoCfg-------------')


    def _testIsDeviceAutoCfgedByRule(self):
        '''
        This function is to test whether FM marks a device as "Auto Configured" with "check" symbol
        '''
        logging.info('-------------Start: _testDeviceIsAutoCfgByRule-------------')
        a = self.aliases
        logging.info('Test to make sure tested devices are auto configured by the expected rule')
        self.errmsg = ''
        idx = 0
        for ap in self.test_aps:
            logging.info('Testing for AP ip: %s, serial: %s' % (ap['ip_addr'], ap['new_serial']))
            try:
                # If test_type is serialBase, the cfg_rule_name is a list of rules
                # Should re-write this case to make it simple
                cfg_rule_name = self.p['cfg_rule_name'] if self.p['test_type'] != 'serialBase' \
                                else self.p['cfg_rule_name'][idx]

                if not a.fm.is_device_auto_configured_by_rule(serial=ap['new_serial'],\
                            cfg_rule_name=cfg_rule_name):
                    self.errmsg += 'ERROR: The device with serial %s is not auto configured by the rule %s' %\
                                   (ap['new_serial'], cfg_rule_name)
                else:
                    logging.info('CORRECT! The device with serial %s is auto configured by the first rule %s' %\
                                     (ap['new_serial'], cfg_rule_name))

                if self.p['test_type'].lower() == 'prioritycheck':
                    if a.fm.is_device_auto_configured_by_rule(serial=ap['new_serial'],\
                            cfg_rule_name=self.p['ex_cfg_rule_name']):
                        self.errmsg += 'ERROR: The device with serial %s should not be auto configured by the second rule %s' %\
                                        (ap['new_serial'], self.p['ex_cfg_rule_name'])
                    else:
                        logging.info('CORRECT! The device with serial %s is not auto configured by the second rule %s' %\
                                     (ap['new_serial'], self.p['ex_cfg_rule_name']))
            except Exception, e:
                self.errmsg += e.__str__()
            idx +=1

        if self.errmsg: logging.info(self.errmsg)
        logging.info('-------------Finish: _testDeviceIsAutoCfgByRule-------------')


    def _classifyErrMsg(self, **kwa):
        '''
        This function is to classify error message for Normal, Registered AP, and priorityCheck test
        kwa:
        - device: 'ip address of test device'
        '''
        if self.p['test_type'] == 'normal':
            if self.errmsg != '':
                logging.info('ERROR: %s' % self.errmsg)
            else:
                logging.info('All APs are auto configured successully')
        elif self.p['test_type'] == 'registeredAp':
            if self.COMPARISON_PHRASE in self.errmsg:
                logging.info('Found expected difference for registered AP test. Detail: %s' % self.errmsg)
                self.errmsg = ''
            else:
                logging.info('ERROR: %s' % self.errmsg)
        elif self.p['test_type'] == 'priorityCheck':
            if self.errmsg == '':
                self.errmsg += 'ERROR: The late auto config rule %s did configure for the test AP %s' %\
                              (self.p['ex_cfg_rule_name'], kwa['device'])
            else:
                logging.info('Found expected difference for priority check. Detail: %s' % self.errmsg)
                self.errmsg = ''


    def _testAPCfgs(self):
        logging.info('------------------Start: _testAPCfgs------------------')
        a, self.errmsg, MAX_RETRIES = self.aliases, '', 3
        logging.info('Test the AP Provisioned Config for model %s' % self.p['model'])

        # Remove un-neccessary items in wlan detail before doing compare before FM and AP config
        # In the future will add better code to remove all nesscessa
        logging.info('Add/Remove items before doing compare')
        fm_cfg_options = self._add_removeSometemsForComparison(**self.p['options'])

        for ap in self.test_aps:
            for i in try_times(MAX_RETRIES, 20):
                self._waitForAPResourceAvailable()
                try:
                    ap_map_func = {
                        'device_general': ap['ap_webui'].get_device_items,
                        'wlan_common': ap['ap_webui'].get_wlan_common_items,
                        'wlan_1': ap['ap_webui'].get_wlan_det_items,
                        'wlan_2': ap['ap_webui'].get_wlan_det_items,
                        'wlan_3': ap['ap_webui'].get_wlan_det_items,
                        'wlan_4': ap['ap_webui'].get_wlan_det_items,
                        'wlan_5': ap['ap_webui'].get_wlan_det_items,
                        'wlan_6': ap['ap_webui'].get_wlan_det_items,
                        'wlan_7': ap['ap_webui'].get_wlan_det_items,
                        'wlan_8': ap['ap_webui'].get_wlan_det_items,
                    }

                    ap['ap_webui'].start(5) # work around to fix the error ap cannot start
                    for k,v in fm_cfg_options.iteritems():
                        if v != None:
                            ap_info = ap_map_func[k](**v) # Base on items of v to get those info from ap
                            msg = self._compareTwoDicts(**{'FM':v, 'AP':ap_info})
                            if msg != '' :
                                self.errmsg += k + ': ' + msg + '\n'
                            del ap_info

                    if self.p['test_type'].lower() == 'prioritycheck':
                        # If the first rule cannot apply its auto config rule, exit
                        if self.errmsg != '':
                           self.errmsg = 'ERROR: The first rule cannot do auto config for AP %s. Detail: %s' %\
                                         (ap['ip_addr'], self.errmsg)
                           logging.info(self.errmsg)
                           return

                        ex_fm_cfg_options = self._add_removeSometemsForComparison(**self.p['ex_options'])
                        for k,v in ex_fm_cfg_options.iteritems():
                            if v != None:
                                ap_info = ap_map_func[k](**v) # Base on items of v to get those info from ap
                                msg = self._compareTwoDicts(**{'FM':v, 'AP':ap_info})
                                if msg != '' :
                                    self.errmsg += k + ': ' + msg + '\n'
                                    break
                                del ap_info

                        # After comparing all configured items of ex_options, if there is no error message in
                        # errmsg => The second auto config rule is applied for test APs => Error
                    ap['ap_webui'].stop()
                    self._classifyErrMsg(device=ap['ip_addr'])
                    if self.errmsg != '': return
                    break
                except Exception:
                    # Whenever an exception error occurs due to cannot start webui,
                    # cannot get some items on webui. We will re-try by re-monitoring
                    # AP CPU then try again
                    self.errmsg += traceback.format_exc()
                    if i < MAX_RETRIES:
                        self.errmsg = ''
                        logging.info('Some weird error happens. Try again...')

        if self.errmsg == '':
            logging.info('All APs auto configured successfully')
        else:
            logging.info('ERROR: %s' % self.errmsg)

        logging.info('------------------Finish: _testAPCfgs------------------')


    def _doVerifyAutoCfgForNormalTest(self):
        '''
        This function is to call two functions _testFMMarksDeviceAsAutoCfg, and _testAPCfgs
        to verify the result
        '''
        self._testFMMarksDeviceAsAutoCfg()
        if self.errmsg != '': return

        self._testIsDeviceAutoCfgedByRule()
        if self.errmsg != '': return

        self._testAPCfgs()
        if self.errmsg != '': return


    def _findAutoCfgTagFromDeviceReg(self):
        '''
        This function is to make sure the test devices having auto configured tag as we did
        '''
        a = self.aliases
        logging.info('Test the Auto Configured Tag for model %s' % self.p['model'])
        self.errmsg = ''
        for ap in self.test_aps:
            if not a.fm.find_device_auto_configured_tag(serial=ap['new_serial'], tag=ap['tag']):
                self.errmsg += 'Fail: Not Found an expected Auto Configured Tag "%s" for device ip: "%s", serial "%s"\n'%\
                            (ap['tag'], ap['ip_addr'], ap['new_serial'])


    def _findTagNameFromManageDevice(self):
        '''
        This function is to find Tag Name for test devices in a group in Manage Devices page
        to make sure they have expected value
        '''
        a = self.aliases
        logging.info('Test the Tag Name for model %s' % self.p['model'])
        self.errmsg = ''
        for ap in self.test_aps:
            if not a.fm.find_device_tag_name_from_manage_device(serial=ap['new_serial'], \
                                                      tag=ap['tag'], group=self.p['device_group']):
                self.errmsg += 'Fail: Not Found the expected Tag Name "%s" for device ip: "%s", serial "%s"\n'%\
                            (ap['tag'], ap['ip_addr'], ap['new_serial'])


    def _doVerifyAutoCfgForPreRegTest(self):
        '''
        This function is to call two functions _testFMMarksDeviceAsAutoCfg, and _testAPCfgs
        to verify the result
        '''
        # Sometimes this step failed so we retry it several times
        MAX_RETRIES = 3
        retry = 1
        while retry <= MAX_RETRIES:
            try:
                self._findAutoCfgTagFromDeviceReg()
                if self.errmsg and retry < MAX_RETRIES:
                    if retry < MAX_RETRIES:
                        self.errmsg = ''
                        time.sleep(10)
                    retry +=1
                    continue

                self._findTagNameFromManageDevice()
                if self.errmsg:
                    if retry < MAX_RETRIES:
                        self.errmsg = ''
                        time.sleep(10)
                    retry +=1
                    continue
            except Exception:
                if retry < MAX_RETRIES:
                    self.errmsg = ''
                    time.sleep(10)
                retry +=1
                continue
            break


    def _rebootAndWaitApBootUp(self):
        '''
        To reboot and wait for AP boot up. This function is to make sure AP calls home immediately.
        '''
        self.errmsg = ''
        config = get_ap_default_cli_cfg()
        for ap in self.test_aps:
            config['ip_addr'] = ap['ip_addr']
            if not reboot_ap(config):
                self.errmsg = 'Error: Cannot reboot AP %s to make it calls home immediately' % ap['ip_addr']
                logging.info(self.errmsg)
                return

        for ap in self.test_aps:
            config['ip_addr'] = ap['ip_addr']
            #config['timeout'] =
            if not wait4_ap_up(config=config):
                self.errmsg = 'Error: AP %s rebooted but it does not come up' % ap['ip_addr']
                logging.info(self.errmsg)
                return


    def _initRegisteredApTest(self):
        '''
        To init test for tcs:
        1.1.7.3.1.9    Already registrer AP test

        - cfg_rule_name
        - device_group: group of devices to aplly this rule
        - model: model to apply this rule
        - cfg_template_name: The template for this rule
        '''
        logging.info('--------------Start: _initNormalTest---------------')
        self.errmsg = ''
        logging.info('Creating a new config template for the test...')
        # Create a new configuration template
        self._createCfgTemplate()

        # init the groupt for this rule
        self.p['device_group'] = 'All Standalone APs'
        logging.info('Apply the rule for group %s' % self.p['device_group'])


    def _doRegisteredApTest(self):
        '''
        This function will do main steps
            1. Create an auto config rule
            2. Set FM url for each AP, to make sure AP sends informessage to FM
            2. Wait for FM applies auto config to FM. Actually, this step is just a procedure for
               this kind of test.
        Note: This test needn't change AP serial.

        '''
        # 1. Create an auto config rule
        self._cfgAutoCfgRule()
        if self.errmsg !='': return

        # Reboot to force AP calls home immmediately
        self._rebootAndWaitApBootUp()
        if self.errmsg !='': return

        self._waitForAPResourceAvailable()
        if self.errmsg !='': return


    def _doVerifyAutoCfgForRegisteredAp(self):
        '''
        This function is to test for the case we have an auto config rule and it is
        to make sure this rule doesn't apply for APs which already registered to FM
        before the rule created.
        '''
        exp_errmsg = "has difference"
        self._testAPCfgs()

        # if the error message has phrase "self.COMPARISON_PHRASE", it means the test passes.
        # The rule doesn't re-config for register APs
        if self.COMPARISON_PHRASE in self.errmsg:
            logging.info('Found expected error message. %s' % self.errmsg)
            self.errmsg = ''
            return

    def _doRestoreForRegisteredApTest(self):
        '''
        This function is to do following thing:
            1. Stop auto config rule
        '''
        err_msg = ''
        self._stopApCfgRule()
        if self.errmsg !='': err_msg += self.errmsg

        # TODO: Whether we should consider restore original config for test APs if this test fails and
        # FM apply the auto config for them?? In this test we only re-config "device_name" so it may be
        # too important to restore the default config for the test APs

        self.errmsg = err_msg


    def _compareTwoDicts(self, **kwargs):
        '''
        This function is to compare values of two dictionaries. Note, two dictionaries
        have the same keys.
        '''
        items = {
            'FM':"",
            'AP':"",
        }
        items.update(kwargs)

        msg = ''
        for k in items['FM'].iterkeys():
            if items['FM'][k].lower() != items['AP'][k].lower():
                msg += self.DIFF_CFG_MSG % (k, items['FM'][k],items['AP'][k])
                #return False

        return msg


    def _add_removeSometemsForComparison(self, **kwargs):
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
        a = self.aliases

        # Remove unnecessary forr wlan 1 to 8
        for i in range(1,9):
            k = 'wlan_%d' % i

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
        k = 'device_general'
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
                'initTest': self._initNormalTest,
                'executeMainJob': self._doNormalTest,
                'followUpTask': self._monitor_device_registration,
                'testTheResults': self._doVerifyAutoCfgForNormalTest,
                'restoreCfg': self._doRestoreForNormalTest,
            },
            'registeredAp': {
                'initTest': self._initRegisteredApTest,
                'executeMainJob': self._doRegisteredApTest,
                'followUpTask': None,
                'testTheResults': self._doVerifyAutoCfgForRegisteredAp,
                'restoreCfg': self._doRestoreForRegisteredApTest,
            },
            # This test is the same normal test
            'priorityCheck': {
                'initTest': self._initNormalTest,
                'executeMainJob': self._doNormalTest,
                'followUpTask': self._monitor_device_registration,
                'testTheResults': self._doVerifyAutoCfgForNormalTest,
                'restoreCfg': self._doRestoreForNormalTest,
            },
            # This test is the same normal test
            'serialBase': {
                'initTest': self._initNormalTest,
                'executeMainJob': self._doNormalTest,
                'followUpTask': self._monitor_device_registration,
                'testTheResults': self._doVerifyAutoCfgForNormalTest,
                'restoreCfg': self._doRestoreForNormalTest,
            },
            'pre-Registration': {
                'initTest': self._initPreRegTest,
                'executeMainJob': self._doNormalTest, #self._doPreRegTest,
                'followUpTask': self._monitor_device_registration,
                'testTheResults': self._doVerifyAutoCfgForPreRegTest,
                'restoreCfg': self._doRestoreForNormalTest,
            },
        }[kwa['test_type']]


    def _setApFmUrl(self):
        '''
        This function is to set FM server url for each AP
        '''
        a = self.aliases
        self.errmsg = ''
        fm_url = 'https://%s/intune/server' % a.fm.config['ip_addr']
        self._waitForAPResourceAvailable()
        for ap in self.test_aps:
            try:
                ap['ap_webui'].start(tries=15)
                #callhome_interval = ap['ap_webui'].set_call_home_interval(interval=ap['ap_webui'].CallHomeIntervalMin)
                #ap['ap_webui'].set_fm_url(url=fm_url, validate_url=False)
                acc_lib.set(
                    ap['ap_webui'],
                    cfg=dict(remote_mode='auto', fm_url=fm_url, inform_interval='5ms')
                )
                logging.info('AP: %s, FM server url: %s'  % \
                              (ap['ap_webui'].config['ip_addr'], fm_url)) #, callhome_interval: %s, callhome_interval))
            except Exception:
                self.errmsg += traceback.format_exc()
                logging.debug(self.errmsg)

            ap['ap_webui'].stop()

        self._waitForAPResourceAvailable()


