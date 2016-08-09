'''
Testsuite
1.1.7.3.2    Auto Configuation rule created test
1.1.7.3.2.1    If the product type is different between template and autoconfiguration model type , System will display a error message after save this auto configuration rule.
1.1.7.3.2.2    Create many auto configuration rule(maybe over 256) and check all of rules can work properly.
1.1.7.3.2.3    User can stop auto configuration task
1.1.7.3.2.4    User can re-start auto configuration task after stop auto configuration task

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


Parameters for each test:
    stressTest:
        'no_rule': 256, # This para is used only for stressTest tc
        '2925_options': {}, # stressTest param: used to create 2925 template
        '2942_options': {}, # stressTest param: used to create 2942 template
        '7942_options': {}, # stressTest param: used to create 7942 template

'''

import time
import logging
import copy
from pprint import pformat

from RuckusAutoTest.common.utils import get_timestamp, log_trace, log_cfg, try_times
from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.fm.lib_FM import get_ap_serial, set_ap_serial, set_ap_factory, \
        get_ap_default_cli_cfg, wait4_ap_up, wait4_ap_stable, \
        FailMessages, reboot_ap
from RuckusAutoTest.components import Helpers as lib


class FM_AutoCfgRuleCreatedTest(Test):
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

        if self.steps['testTheResults']: self.steps['testTheResults']()
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

            for ap in self.test_aps:
                #ap._tmp_.pop(self.timestamp)
                del ap

            a.fm.logout()
        except Exception:
            log_trace()


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
            'test_type': 'validateInputData',
            'device_group': 'All Standalone APs',
            'options': {},
            'tag': '', # this para is only used for preg-Registration test
            'no_rule': 256, # This para is used only for stressTest tc
            '2925_options': {}, # stressTest param: used to create 2925 template
            '2942_options': {}, # stressTest param: used to create 2942 template
            '7942_options': {}, # stressTest param: used to create 7942 template
            '7962_options': {}, # stressTest param: used to create 7962 template
        }
        self.p.update(kwa)
        self.p['model'] = self.p['model'].upper()

        logging.info('Init for the test "%s"' % self.p['test_type'])
        self._cfgSteps(test_type=self.p['test_type'])

        self.timestamp = get_timestamp()

        self.test_aps = self._getAndInitAffectedAps(**self.p)

        # init a variable for stress test
        if self.p['test_type'] == 'stressTest':
            # this one is a list of pair of device group and rule name
            self.stress_test_info = []
            # rule_info is elementof stress_test_info
            rule_info = {
                'cfg_template_name': '',
                'cfg_rule_name': '',
                'device_group': '',

                'serial': '',
                'ip_addr': '',
                'ap_webui': None, # ap webui instance
                'options': '',
                'test_done': False,
            }
            # init place holder for the stressTest
            for i in range(self.p['no_rule']):
                new_item = copy.deepcopy(rule_info)
                self.stress_test_info.append(new_item)

        # No need auto config rule for "pre-Registration" test
        if self.p['test_type'] != 'stressTest':
            self._create_auto_cfg_ruleName()

        #if self.steps['updateTestParams']: self.steps['updateTestParams']()
        logging.debug('TestConfig:\n%s' % pformat(self.p))


    def _create_auto_cfg_ruleName(self):
        '''
        This function is base on test_type to create auto config rule for the test
        '''
        self.p['cfg_rule_name'] = 'Auto_Cfg_%s_%s' % (self.p['model'], self.timestamp)


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
        test_aps = []
        if self.p['test_type'] == 'stressTest':
            # Get all aps (ip_addr, model...) registered to FM
            logging.info('Get all supported AP model for the stressTest')

            supported_models, no_init_ap = ['zf2925', 'zf2942', 'zf7942'], 0
            tb_aps  = a.fm.get_all_aps()
            for i in range(len(tb_aps)):
                # in case a number of aps in the test bed is more than no of rules need to be tested
                if no_init_ap >= self.p['no_rule']: break
                # To avoid get model not supported to create its config template
                if not (tb_aps[i]['model'].lower() in supported_models): continue

                tmp_cfg = copy.deepcopy(ap_cfg)
                config= {
                    'ip_addr': tb_aps[i]['ip_addr']
                }
                tmp_cfg = {
                    'ap_webui': a.tb.getApByIp(tb_aps[i]['ip_addr']),
                    'ip_addr': tb_aps[i]['ip_addr'],
                    'model': tb_aps[i]['model'],
                    'ori_serial': get_ap_serial(**{'config':config}),
                    'new_serial': '',
                }
                test_aps.append(tmp_cfg)
                no_init_ap +=1
        else:
            logging.info('Get and init all affected Aps (model=%s)' % kwa['model'])
            aps = a.tb.getApByModel(kwa['model'])
            if len(aps) == 0: raise Exception(FailMessages['NoApFoundWithInputModel'] % kwa['model'])

            for ap in aps:
                ap.init_temp_storage(timestamp=self.timestamp)
                tmp_cfg = copy.deepcopy(ap_cfg)
                config= {
                    'ip_addr': ap.config['ip_addr'],
                }
                tmp_cfg = {
                    'ap_webui': ap,
                    'ip_addr': ap.config['ip_addr'],
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
        self.ApCfgTimeOut = 3 # mins
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
        except Exception, e:
            self.errmsg = 'Failed to create a template %s for the test. Error: %s' % \
                          (fm_cfg_template['template_name'], e)
            log_trace()
        logging.info('--------------Finish: _createCfgTemplate---------------')


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
            self.errmsg = 'Cannot generate new serials for the test. Error: %s' % e
            log_trace()
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
        self.errmsg = ''
        logging.info('Creating a new config template for the test...')
        # Create a new configuration template
        self._createCfgTemplate()
        if self.errmsg != '': return

        self._cfgAutoCfgRule()
        if self.errmsg != '': return

        logging.info('Test device groups %s' % self.p['device_group'])


    def _getDifferentModel(self):
        '''
        This function is to return a different model to do validate input data test
        '''

        # test_models = ['zf2925', 'zf2942', 'zf7942']
        # timeout = 30
        # endtime = time.time() + endtime
        # while time.time() < endtime:
        #     idx = random.randint(0, len(test_models)-1)
        #     if self.p['model'] == test_aps[idx]:
        #         continue
        #     return test_aps[idx]

        # raise Exception("")

        if self.p['model'].lower() == 'zf2925':
            return 'zf2942'
        elif  self.p['model'].lower() == 'zf2942':
            return 'zf7942'
        else:
            return 'zf2925'


    def _initValidateInputDataTest(self):
        '''
        To init test for tcs:
        1.1.7.3.2.1    If the product type is different between template and autoconfiguration model type , System will display a error message after save this auto configuration rule.

        - cfg_rule_name
        - device_group: group of devices to aplly this rule
        - model: model to apply this rule
        - cfg_template_name: The template for this rule
        '''
        logging.info('--------------Start: _initValidateInputDataTest---------------')
        self.errmsg = ''
        # Create a new configuration template
        self._createCfgTemplate()
        if self.errmsg != '': return
        logging.info('Created a new config temmplate "%s" for the test' % self.p['cfg_template_name'])

        logging.info('--------------Finish: _initValidateInputDataTest---------------')


    def _doValidateInputDataTest(self):
        '''
        This function is to do validate consistency between template and auto config model type.
        '''
        logging.info('-------------Start: _doValidateInputDataTest-------------')
        a = self.aliases
        exp_msg = 'Model & Template are not matched'
        self.errmsg = ''
        logging.info('Configure an Auto Config Rule for model %s' % self.p['model'])
        try:
            #Other tests: normal, registeredAp, priorityCheck
            model = self._getDifferentModel()
            cfg = {
                    'cfg_rule_name': self.p['cfg_rule_name'],
                    'device_group': self.p['device_group'],
                    'model': model.upper(),
                    'cfg_template_name': self.p['cfg_template_name'],
            }
            logging.info('Creating a new auto config rule "%s"' % self.p['cfg_rule_name'])
            a.fm.create_auto_cfg_rule(**cfg)
            self.errmsg = 'ERROR: Do not find any error message while creating a rule with template model ' \
                          '"%s" and auto config model "%s"' % (self.p['model'], model)
        except Exception, e:
            if exp_msg in e.__str__():
                logging.info('Found expected error message "%s" for template model "%s" and auto config model "%s"' %\
                            (exp_msg, self.p['model'], model))
            else:
                self.errmsg = e.__str__()

        if self.errmsg != '': logging.info(self.errmsg)
        logging.info('-------------Finish: _doValidateInputDataTest-------------')


    def _doRestoreForValidateInputDataTest(self):
        '''
        This function is to do following thing:
            1. Remove the template created for the test
        '''
        logging.info('-------------Start: _doRestoreForValidateInputDataTest-------------')
        a = self.aliases
        self.errmsg = ''
        try:
            logging.info("Deleting the template: %s" % self.p['cfg_template_name'])
            a.fm.delete_cfg_template_by_name(self.p['cfg_template_name'])
        except Exception:
            self.errmsg = 'Cannot delete the configuration template %s' % self.p['cfg_template_name']
            logging.info(self.errmsg)

        logging.info('-------------Finish: _doRestoreForValidateInputDataTest-------------')


    def _initStressTest(self):
        '''
        This function is to init for tc
        1.1.7.3.2.2    Create many auto configuration rule(maybe over 256) and check all of rules can work properly.
        '''
        logging.info('--------------Start: _initStressTest---------------')
        self.errmsg = ''
        logging.info('Creating a new config template for the test...')
        # Create a new configuration template
        self._createCfgTemplateForStressTest()
        if self.errmsg != '': return

        logging.info('Generating new unique AP serials for the test...')
        # Create new serial for a list of tested APs
        self._generateNewSerialsForStressTest()
        if self.errmsg != '': return

        logging.info('--------------Finish: _initStressTest---------------')


    def _generateNewSerialsForStressTest(self):
        '''
        Base on number of rules for stressTest to create new serials respectively
        '''
        logging.info('--------------Start: _generateNewSerialsForStressTest---------------')
        self.errmsg = ''
        a = self.aliases
        try:
            no_serials = int(self.p['no_rule'])
            self.test_serials = a.fm.generate_unique_ap_serials(**{'no': no_serials, 'prefix': 'ZF'})
            #for i in self.p['no_rule']:
            #    self.stress_test_info[i]['serial'] = test_serial[i]

            logging.info('List of serials generated for stressTest: %s' % self.test_serials)
        except Exception, e:
            self.errmsg = 'Cannot generate new serials for the test. Error: %s' % e
            log_trace()

        logging.info('--------------Finish: _generateNewSerialsForStressTest---------------')


    def _createCfgTemplateForStressTest(self):
        '''
        This function is base on how many APs are available on the test bed to create new config templates
        respectively.
        '''
        logging.info('--------------Start: _createCfgTemplate---------------')
        self.errmsg = ''
        a = self.aliases

        try:
            i = 1
            for ap in self.test_aps:
                ap['cfg_template_name'] = 'Auto_Cfg_' + ap['model'] +'_' + self.timestamp + '_%02d' % i
                #self.p['cfg_template_name'] = 'Auto_Cfg_' + self.p['model'] +'_' + self.timestamp
                # after this step, each test_aps will has a new key "options"
                ap['options'] = {
                    'zf2925': self.p['2925_options'],
                    'zf2942': self.p['2942_options'],
                    'zf7942': self.p['7942_options'],
                    'zf7962': self.p['7962_options'],
                }[ap['model'].lower()]
                #ap['options'] = map_opts

                fm_cfg_template = {
                    'template_name': ap['cfg_template_name'],
                    'template_model': ap['model'].upper(), # map_template_model,
                    'options': ap['options'],
                    'convert_in_advanced': True,
                }
                #a.fm.create_cfg_template(**fm_cfg_template)
                lib.fm.cfg_tmpl.create_cfg_tmpl_2(
                    a.fm, fm_cfg_template['template_name'],
                    fm_cfg_template['template_model'], fm_cfg_template['options']
                )
                logging.info('Created a new configuration template %s for the test successfully' % ap['cfg_template_name'])
                i +=1
        except Exception, e:
            log_trace()
            self.errmsg = 'Error occurs while creating template for the stress '\
                          'test. Error: %s' % e

        if self.errmsg: logging.info(self.errmsg)
        logging.info('--------------Finish: _createCfgTemplate---------------')


    def _create_auto_cfg_ruleNameForStressTest(self):
        '''
        This function is base on test_type to create auto config rule for the the stress test
        '''
        for i in range(self.p['no_rule']):
            info = copy.deepcopy(self.rule_info)
            # rule = 'Auto_Cfg_%s_%s_%03d' % (self.p['model'], self.timestamp, i+1)
            info['rule'] = 'Auto_Cfg_%s_%s_%03d' % (self.p['model'], self.timestamp, i+1)
            self.stress_test_info.append(info['rule'])


    def _createDeviceGroupForStressTest(self):
        '''
        This function is to create device group for stressTest test
        # Create a group base new serial
        # For this test: If our system has a few of APs 2925 or 2942 or 7942, we will create each group for each AP.
        # Ex: we have two ZF2925s, => Create two groups base on their serials for each 2925.
        '''
        a, self.errmsg = self.aliases, ''
        idx = 0
        for item in self.stress_test_info:
            found_fail, idx = True, idx+1
            for i in try_times(10, 3):
                try:
                    logging.info('%03d: Creating a new device group for serial %s' % (idx, item['serial']))
                    a.fm.create_serial_group(serial=item['serial'], name=item['device_group'])
                    # sleep a moment before creating a next one
                    time.sleep(2)
                    found_fail = False
                    break;
                except:
                    found_fail= True
                    logging.info('Cannot create device groups base on serial %s. Try again...'
                                 % item['serial'])
                    log_trace()
            if found_fail:
                self.errmsg = 'ERROR: Cannot create enough device groups base on' \
                              ' serial for stressTest. Break the test!'
                logging.info(self.errmsg)
                break

    def _setNecessaryInfoForStressTest(self):
        '''
        This function is to add necessary information (model, ap ip_addr, cfg_template_name, ap_webui instance,)
        for each rule for the stressTest.
        '''
        ap_idx = 0
        for i in range(len(self.stress_test_info)):
            if ap_idx >= len(self.test_aps):
                    # The idea is that we rotate all aps in the testbed for each rule
                    # so that we do test all ap to share workload for each ap
                    # reset ap_idx
                    ap_idx = 0

            # assign model and ip_addr of ap for each element, this infor will be used
            # to change AP serial to force it register to FM for the tests
            self.stress_test_info[i]['ap_webui'] = self.test_aps[ap_idx]['ap_webui']
            self.stress_test_info[i]['serial'] = self.test_serials[i]
            self.stress_test_info[i]['model'] = self.test_aps[ap_idx]['model']
            self.stress_test_info[i]['ip_addr'] = self.test_aps[ap_idx]['ip_addr']
            self.stress_test_info[i]['cfg_rule_name'] = 'Auto_Cfg_%s_%s_%03d' % \
                                                        (self.stress_test_info[i]['model'], self.timestamp, i+1)
            self.stress_test_info[i]['create_time'] = 'create time of the rule'
            self.stress_test_info[i]['cfg_template_name'] = self.test_aps[ap_idx]['cfg_template_name']
            self.stress_test_info[i]['device_group'] = "Group_Serial_" + self.stress_test_info[i]['serial']
            self.stress_test_info[i]['options'] = self.test_aps[ap_idx]['options']

            ap_idx += 1


    def _cfgAutoCfgRuleForStressTest(self):
        '''
        Create an auto configuration rule for this group
        '''
        a = self.aliases
        self.errmsg = ''
        logging.info('Configure an Auto Config Rule for model %s' % self.p['model'])
        log_cfg(self.p)
        for item in self.stress_test_info:
            # assign model and ip_addr of ap for each element, this infor will be used
            # to change AP serial to force it register to FM for the tests
            cfg = {
                    'cfg_rule_name': item['cfg_rule_name'],
                    'device_group': item['device_group'],
                    'model': item['model'].upper(),
                    'cfg_template_name': item['cfg_template_name'],
                    'advance_return': True, # get the create time of each auto config rule
            }
            for i in try_times(10, 3):
                try:
                    create_time = a.fm.create_auto_cfg_rule(**cfg)
                    break;
                except Exception:
                    log_trace()
                    logging.info('Fail to create rule %s' % cfg['cfg_rule_name'])

            # Update create time for this rule
            item['create_time'] = create_time
            logging.info('Created an auto config rule: "%s", create time: %s for the test. Detail: %s' % \
                         (item['cfg_rule_name'], create_time, cfg))
            time.sleep(3)


    def _setNewApSerial(self, **kwa):
        '''
        Change ap serial of ap given in kwa
        kwa:
        - serial: serial to change it to
        - ip_addr: ip of ap to reset the serial
        '''
        config= {
            'ip_addr': kwa['ip_addr']
        }
        MAX_TIME, is_success, self.errmsg = 10, True, ''

        logging.info('Change serial of AP %s to %s' % (kwa['ip_addr'], kwa['serial']))
        for i in try_times(MAX_TIME, 3):
            try:
                is_success = True
                if not set_ap_serial(**{'serial': kwa['serial'], 'config': config}):
                    is_success = False

                if is_success and not reboot_ap(config):
                    is_success = False

                if is_success: break
            except Exception, e:
                self.errmsg = 'Error while set a new serial %s for AP %s. Try again...!' % \
                    (kwa['serial'], kwa['ip_addr'])
                log_trace()

        if not is_success:
            self.errmsg = 'Cannot set a new serial %s for AP %s after trying %s times' %\
                          (kwa['serial'], kwa['ip_addr'], MAX_TIME)
            logging.info(self.errmsg)


    def _doStressTest(self):
        '''
        This function will do main steps
            1. Create an auto config rule
            2. Change AP serial so that AP will register to FM with new serial
            3. Wait for FM applies auto config to FM.

            self.stress_test_info[i]['ap_webui'] = self.test_aps[ap_idx]['ap_webui']
            self.stress_test_info[i]['serial'] = self.test_serials[i]
            self.stress_test_info[i]['model'] = self.test_aps[ap_idx]['model']
            self.stress_test_info[i]['ip_addr'] = self.test_aps[ap_idx]['ip_addr']
            self.stress_test_info[i]['cfg_rule_name'] = 'Auto_Cfg_%s_%s_%03d' % \
                                                        (self.stress_test_info[i]['model'], self.timestamp, i+1)
            self.stress_test_info[i]['cfg_template_name'] = self.test_aps[ap_idx]['cfg_template_name']
            self.stress_test_info[i]['device_group'] = "Group_Serial_" + self.stress_test_info[i]['serial']
            self.stress_test_info[i]['options'] = self.test_aps[ap_idx]['options']
        '''
        self._setNecessaryInfoForStressTest()

        # Create device group after set necessary info for stress test
        self._createDeviceGroupForStressTest()
        if self.errmsg != '': return

        # Create an auto config rule
        self._cfgAutoCfgRuleForStressTest()
        if self.errmsg != '': return

        total_errmsg = ''
        idx = 1
        for item in self.stress_test_info:
            # 2. Change AP serial so that AP will register to FM with new serial
            logging.info('Start testing a rule no: %03d.\n Detail info for the rule:\n' \
                    '\tRule name        : %s\n' \
                    '\tSerial           : %s\n' \
                    '\tmodel            : %s\n' \
                    '\tip_addr          : %s\n' \
                    '\tcfg template name: %s\n' \
                    '\tdevice group     : %s\n' %\
                    (idx,
                     item['cfg_rule_name'],
                     item['serial'],
                     item['model'],
                     item['ip_addr'],
                     item['cfg_template_name'],
                     item['device_group']))
            cfg = {
                'ip_addr': item['ip_addr'],
                'serial': item['serial'],
                'options': item['options'],
                'cfg_rule_name': item['cfg_rule_name'],
                'advance_search': True,
                'create_time': item['create_time'],
            }
            msg = ''
            #1. set serial
            self._setNewApSerial(**cfg)
            if self.errmsg != '':
                msg = self.errmsg + '\n'

            #2. monitor it
            if msg =='':
                self._monitor_device_registration(**cfg)
                if self.errmsg != '':
                    msg = self.errmsg + '\n'

            #3. wait for it provisioning
            if msg == '':
                self._waitForProvisioningAutoCfgToAp(**cfg)
                if self.errmsg != '':
                    msg = self.errmsg + '\n'

            retries, tmp_msg = 1, ''
            # retries three time for a case
            while msg == '' and retries <= 3:
                logging.info('Trying to test %d times' % retries)
                tmp_msg = ''
                #4. do verify: test FM mark device as Auto Config
                if tmp_msg == '':
                    self._testFMMarksDeviceAsAutoCfg(**cfg)
                    if self.errmsg != '':
                        tmp_msg = self.errmsg + '\n'
                        retries +=1
                        continue

                if tmp_msg == '':
                    self._testIsDeviceAutoCfgedByRule(**cfg)
                    if self.errmsg != '':
                        tmp_msg = self.errmsg + '\n'
                        retries +=1
                        continue

                #5. do verify: test ap config
                if tmp_msg == '':
                    self._setApFmUrl(**cfg)

                    self._testAPCfgs(**cfg)
                    if self.errmsg != '':
                        tmp_msg = self.errmsg + '\n'
                        retries +=1
                        continue
                # if reach this position, no error happens. break the loop
                break
            '''
            # No need to set factory at this step. When begin a new test for a new serial,
            # it will be reset factory
            #6 set ap factory to restore its original config
            time.sleep(15)
            if not set_ap_factory(config=cfg):
                msg += 'Cannot set factory default for AP %s\n' % cfg['ip_addr']
            # After changeApSerial, the Ap usually uses DHCP option 43 to contact FM and the AP
            # will be configured automatically
            time.sleep(10)
            '''
            msg += tmp_msg
            logging.info('Finish testing for no: %03d.' % idx)
            idx +=1
            item['test_done'] = True

            if msg != '':
                #self.errmsg = msg
                total_errmsg += msg + '\n\t'
                logging.info(self.errmsg + '\nContinue test other rules...')
                # no break it, let it continue to test other rules
                #break

            if (idx % 20) == 0:
                logging.info('Pending the testing 15 mins to decrease temperature of APs...')
                time.sleep(900)

        self.errmsg = total_errmsg
        logging.info('Total error message for stressTest: %s' % total_errmsg)
        logging.info('Complete stressTest')


    def _doRestoreForStressTest(self):
        '''
        This function is to do following thing:
            1. Stop auto config rule
            2. Deny AP with new serial
            3. Restore original AP serial
        '''
        msg = ''
        logging.info('Do restore for stressTest')
        self._stop_auto_cfg_rulesForStressTest()
        if self.errmsg != '': msg += self.errmsg

        self._disableDevicesWithNewSerialForStressTest()
        if self.errmsg != '': msg += self.errmsg

        self._restoreApSerial()
        if self.errmsg != '': msg += self.errmsg

        self._waitForAPResourceAvailable()

        self._setApFmUrl()
        if self.errmsg != '': msg += self.errmsg

        self.errmsg = msg
        if self.errmsg != '': logging.info(self.errmsg)


    def _stop_auto_cfg_rulesForStressTest(self):
        '''
        To stop an auto cfg rule
        '''
        logging.info('Stop auto config rule created for stressTest')
        a, self.errmsg = self.aliases, ''

        for item in self.stress_test_info:
            try:
                # r_cfg = self.p['cfg_rule_name']
                logging.info('Trying to delete the rule %s' % item['cfg_rule_name'])
                lib.fm.auto_cfg.delete_auto_cfg_rule(
                    a.fm, item['cfg_rule_name'], item['create_time']
                )
            except Exception, e:
                logging.info(
                    'Warning: Cannot delete the rule %s. Error: %s. Try to stop it' %
                    (item['cfg_rule_name'], e.__str__())
                )
                try:
                    lib.fm.auto_cfg.stop_auto_cfg_rule(
                            a.fm, item['cfg_rule_name'], item['create_time']
                    )
                except:
                    logging.info(
                        'Warning: Cannot stop the rule %s. Error: %s' %
                        (item['cfg_rule_name'], e.__str__())
                    )

        if self.errmsg != '': logging.debug(self.errmsg)


    def _disableDevicesWithNewSerialForStressTest(self):
        '''
        After finish the test we need to disable tested APs with new serial
        so that they are not shown on Inventory > Manage Device
        '''
        # print '-----------Start: _disableDevicesWithNewSerialForStressTest-------------'

        logging.info('Disable devices with new serials created for stressTest')
        a = self.aliases
        self.errmsg = ''
        for item in self.stress_test_info:
            if not item['test_done']: break
            cfg = {
                'serial': item['serial'],
                'status': 'Unavailable',
                'comment': 'Automation changed to Unavailable'
            }
            try:
                a.fm.edit_device_status(**cfg)
            except Exception, e:
                self.errmsg += e.__str__()

        if self.errmsg != '': logging.debug(self.errmsg)

        # print '-----------Finish: _disableDevicesWithNewSerialForStressTest-------------'


    def _doStopAutoCfgRuleTest(self):
        '''
        This function will do main steps
            1. Stop the auto config rule
        '''

        self._stopApCfgRule()
        if self.errmsg !='': return


    def _doRestartAutoCfgRuleTest(self):
        '''
        This function will do main steps
            1. Stop the auto config rule then restart it
        '''

        self._stopApCfgRule()
        if self.errmsg !='': return

        self._restart_auto_cfg_rule()
        if self.errmsg !='': return


    def _cfgAutoCfgRule(self):
        '''
        Create an auto configuration rule for this group
        '''
        # print '-------------Start: _cfgAutoCfgRule-------------'
        a = self.aliases
        self.errmsg = ''
        logging.info('Configure an Auto Config Rule for model %s' % self.p['model'])
        try:
            #Other tests: normal, registeredAp, priorityCheck
            cfg = {
                    'cfg_rule_name': self.p['cfg_rule_name'],
                    'device_group': self.p['device_group'],
                    'model': self.p['model'].upper(),
                    'cfg_template_name': self.p['cfg_template_name'],
                }
            a.fm.create_auto_cfg_rule(**cfg)
            logging.info('Created an auto config rule "%s" for the test' % self.p['cfg_rule_name'])
        except Exception, e:
            self.errmsg = e.__str__()
            logging.info(self.errmsg)

        # print '-------------Finish: _cfgAutoCfgRule-------------'


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

            logging.info('Set factory AP %s' % ap['ip_addr'] )
            if not set_ap_factory(config=config):
                self.errmsg = 'Cannot set factory for AP %s after change its serial' % (ap['ip_addr'])
                logging.info(self.errmsg)
                return

        logging.info('-------------Finish: _changeApSerial-------------')


    def _restoreApSerial(self):
        '''
        Restore ogriginal serials for all APs
        '''
        self.errmsg = ''
        for ap in self.test_aps:
            logging.info('Restoring original serial %s for AP %s' % (ap['ori_serial'], ap['ip_addr']))
            config= {
                'ip_addr': ap['ip_addr']
            }

            if not set_ap_serial(**{'serial': ap['ori_serial'], 'config': config}):
                self.errmsg = 'Cannot restore the original serial %s for AP %s' % (ap['ori_serial'], ap['ip_addr']) + '\n'

            if not set_ap_factory(config=config):
                self.errmsg += 'Cannot set factory for AP %s after restoring its original serial' % (ap['ip_addr']) + '\n'

        if self.errmsg != '': logging.debug(self.errmsg)


    def _stopApCfgRule(self):
        '''
        To stop an auto cfg rule
        '''
        a = self.aliases
        self.errmsg = ''
        try:
            logging.info('Trying to stop the rule %s' % self.p['cfg_rule_name'])
            cfg_rule = self.p['cfg_rule_name']
            a.fm.stop_auto_cfg_rule(cfg_rule_name=cfg_rule)
        except Exception, e:
            self.errmsg = 'Cannot stop the rule %s. Error: %s' % (cfg_rule, e.__str__())
            logging.debug(self.errmsg)

    def _restart_auto_cfg_rule(self):
        '''
        Restart the auto config test
        '''
        a = self.aliases
        self.errmsg = ''
        try:
            cfg_rule = self.p['cfg_rule_name']
            logging.info('Trying to restart the rule %s' % cfg_rule)
            a.fm.restart_auto_cfg_rule(cfg_rule_name=cfg_rule)
        except Exception, e:
            self.errmsg = 'Cannot restart the rule %s. Error: %s' % (cfg_rule, e.__str__())
            logging.debug(self.errmsg)


    def _disableTestedDevicesWithNewSerial(self):
        '''
        After finish the test we need to disable tested APs with new serial
        so that they are not shown on Inventory > Manage Device
        '''
        # print '-----------Start: _disableTestedDevicesWithNewSerial-------------'

        a = self.aliases
        self.errmsg = ''
        for ap in self.test_aps:
            cfg = {
                'serial': ap['new_serial'],
                'status': 'Unavailable',
                'comment': 'Automation changed to Unavailable'
            }
            try:
                a.fm.edit_device_status(**cfg)
            except Exception, e:
                self.errmsg = e.__str__()
                logging.debug(self.errmsg)

        # print '-----------Finish: _disableTestedDevicesWithNewSerial-------------'


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


    def _doRestoreForRestartAutoCfgRuleTest(self):
        '''
        This function is to do following thing:
            1. Stop auto config rule
        '''
        self._stopApCfgRule()
        if self.errmsg != '': return


    def _monitor_device_registration(self, **kwa):
        '''
        This function is monitor either APs in self.test_aps or  a serial give in kwa.
        If the kwa has specific ip_addr, the function only monitor that AP.

        NOTE: Actually, it only monitors device serial but we need the ip_addr para to map
        it to serial para and it also to make this function compatible with other test
        beside stressTest

        kwa:
        - serial
        - ip_addr
        '''
        a, self.errmsg, MAX_TIME, found_ap = self.aliases, '', 10, False
        # monitor the task on FM WebUi, total timeout is given here
        for ap in self.test_aps:
            # in case user provides the ip_addr to monitor
            if kwa.has_key('ip_addr') and kwa['ip_addr'] != ap['ip_addr']:
                continue

            found_ap = True
            monitored_serial = kwa['serial']if kwa.has_key('serial') else ap['new_serial']
            logging.info('Monitoring device registration ip address: %s, serial: %s' % \
                       (ap['ip_addr'], monitored_serial))
            _kwa = {
                'serial': monitored_serial,
                'timeout': self.timeout
            }
            for i in try_times(MAX_TIME, 3):#to avoid exception due to dojo
                try:
                    if a.fm.monitor_device_registration(**_kwa):
                        logging.info('Found a device with serial %s registered to FM' % \
                                  (monitored_serial))
                    else:
                        self.errmsg += 'Cannot find any registered AP with serial %s\n' % monitored_serial
                        logging.debug(self.errmsg)
                    break;
                except Exception:
                    log_trace()
                    logging.info('Exception occurs. Try again...')


            # if the ip_addr is provided, it means monitor only one device so exit the function
            if kwa.has_key('ip_addr'): break

        if not found_ap:
            self.errmsg += '\nCannot find ip "%s" in tested devices' % kwa['ip_addr']

        if self.errmsg != '': logging.info(self.errmsg)


    def _waitForProvisioningAutoCfgToAp(self, **kwa):
        '''
        This function is to wait AP get auto configuration from FM
        kwa:
        - ip_addr: ip address of an ip to wait for provisioning config
        - options: options to provision
        NOTE: add kwa argument to make it compatible with the stressTest
        '''
        _kwa = {
            'ip_addr': None,
            'options': None,
        }
        _kwa.update(kwa)

        cfg = kwa['options']if _kwa.has_key('options') else self.p['options']

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
                if _kwa['ip_addr'] and ap['ip_addr'] != _kwa['ip_addr']: continue

                config = get_ap_default_cli_cfg()
                ap_config = ap['ap_webui'].get_cfg()
                config['ip_addr'] = ap_config['ip_addr']
                config['username'] = ap_config['username'] if not change_username else change_username
                config['password'] = ap_config['password'] if not change_password else change_password
                if not wait4_ap_up(**{'config': config, 'timeout': 6}):
                    self.errmsg += 'Cannot login to AP via cli %s after 6 mins waiting' \
                                    % (config['ip_addr'])
                # check if AP CPU is ready for the test

        self._waitForAPResourceAvailable(username=change_username, password=change_password, ip_addr=_kwa['ip_addr'])


    def _waitForAPResourceAvailable(self, **kwa):
        '''
        This function is to check CPU usage of AP and wait for each ready to test.
        Note: if provide username password, this function will use that username/password
        instead of username/password from ap instance to connect to AP and monitor its CPU usage.
        kwa:
        - username: username to log in test APs
        - password: password to log in test APs
        - ip_addr: ip address is given, this function wait for this ap only
        '''
        _kwa = {
            'username': None,
            'password': None,
            'ip_addr': None,
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
        for ap in self.test_aps:
            if _kwa['ip_addr'] and ap['ip_addr'] != _kwa['ip_addr']: continue

            tb_cfg = ap['ap_webui'].get_cfg()

            ap_cli_config['ip_addr'] = tb_cfg['ip_addr']
            ap_cli_config['username'] = _kwa['username'] if _kwa['username'] else tb_cfg['username']
            ap_cli_config['password'] = _kwa['password'] if _kwa['password'] else tb_cfg['password']

            monitor_cpu_cfg.update({'config': ap_cli_config})
            msg = 'The CPU of AP %s looks free for the test' % ap_cli_config['ip_addr']\
                    if wait4_ap_stable(**monitor_cpu_cfg) else \
                    ('WARNING: The CPU usage of AP %s is still too high' % ap_cli_config['ip_addr'])
            logging.info(msg)


    def _testFMMarksDeviceAsAutoCfg(self, **kwa):
        '''
        This function is to test whether FM marks a device as "Auto Configured" with "check" symbol.
        If the serial, ip_addr is provied, it only check for that ip. Otherwise, check all test devices.

        NOTE: Actually, it only monitors device serial but we need the ip_addr para to map
        it to serial para and it also to make this function compatible with other test
        beside stressTest

        kwa:
        - serial
        - ip_addr
        '''
        logging.info('==============Start: _testFMMarksDeviceAsAutoCfg===============')
        logging.info('Test to make sure tested devices marked as Auto Configured')

        a, self.errmsg, found_ap = self.aliases, '', False
        for ap in self.test_aps:
            if kwa.has_key('ip_addr') and ap['ip_addr'] != kwa['ip_addr']:
                continue
            found_ap = True
            serial = kwa['serial']if kwa.has_key('serial') else ap['new_serial']
            logging.info('Testing for AP ip: %s, serial: %s' % (ap['ip_addr'], serial))

            if not lib.fm.auto_cfg.is_device_marked_auto_config(a.fm, serial):
                self.errmsg += 'The device with serial %s is not auto configured' % serial

            # if the ip_addr is provided, it means we check only one that device so exit the function
            if kwa.has_key('ip_addr'): break

        if not found_ap:
            self.errmsg += '\nCannot find ip address "%s" in the tested devices'
            logging.info(self.errmsg)

        logging.info('==============Finish: _testFMMarksDeviceAsAutoCfg===============')


    def _testIsDeviceAutoCfgedByRule(self, **kwa):
        '''
        This function is to test whether a device is "Auto Configured" by a rule.
        If the serial, ip_addr is provied, it only check for that ip. Otherwise, check all test devices.

        NOTE: Actually, it only monitors device serial but we need the ip_addr para to map
        it to serial para and it also to make this function compatible with other test
        beside stressTest

        kwa:
        - serial
        - ip_addr
        - advance_search
        - create_time
        '''
        _kwa = {'advance_search': False,}
        _kwa.update(kwa)
        logging.info('---------------Start: _testIsDeviceAutoCfgedByRule---------------')
        a = self.aliases
        logging.info('Test to make sure tested devices are auto configured by the expected rule')
        self.errmsg = ''
        found_ap = False
        for ap in self.test_aps:
            if kwa.has_key('ip_addr') and ap['ip_addr'] != _kwa['ip_addr']:
                continue

            found_ap = True
            _kwa['serial'] = kwa['serial']if kwa.has_key('serial') else ap['new_serial']
            logging.info('Testing for AP ip: %s, serial: %s' % (ap['ip_addr'], _kwa['serial']))
            try:
                if not a.fm.is_device_auto_configured_by_rule(**_kwa):
                    self.errmsg += 'ERROR: The device with serial %s is not auto configured by the rule %s' %\
                                   (_kwa['serial'], _kwa['cfg_rule_name'])
                else:
                    logging.info('The device with serial %s is auto configured by the rule %s correctly' %\
                                   (_kwa['serial'], _kwa['cfg_rule_name']))
            except Exception, e:
                self.errmsg += str(e)
                log_trace()

            # if the ip_addr is provided, it means we check only one that device so exit the function
            if _kwa.has_key('ip_addr'): break

        if not found_ap:
            self.errmsg += '\nCannot find ip address "%s" in the tested devices'

        if self.errmsg != '': logging.info(self.errmsg)

        logging.info('---------------Finish: _testIsDeviceAutoCfgedByRule---------------')


    def _setApFmUrl(self, **kwa):
        '''
        This function is to set FM server url for each AP.
        If the ip_addr is provided, set FM url for that only ap
        kwa:
        - ip_addr:
        '''
        # print '-----------Start: _setApFmUrl-------------'
        a = self.aliases
        self.errmsg = ''
        found_ap = False
        fm_url = 'https://%s/intune/server' % a.fm.config['ip_addr']

        for ap in self.test_aps:
            if kwa.has_key('ip_addr') and ap['ip_addr'] != kwa['ip_addr']:
                    continue
            try:
                found_ap = True
                ap['ap_webui'].start(tries=5)
                #callhome_interval = ap['ap_webui'].set_call_home_interval(interval=ap['ap_webui'].CallHomeIntervalMin)
                ap['ap_webui'].set_fm_url(url=fm_url, validate_url=False)

                #logging.debug('AP: %s, FM server url: %s, callhome_interval: %s'  % \
                #              (ap['ap_webui'].config['ip_addr'], fm_url, callhome_interval))
                logging.debug('AP: %s, FM server url: %s'  % \
                              (ap['ap_webui'].config['ip_addr'], fm_url))
            except Exception, e:
                self.errmsg += str(e)
                log_trace()

            ap['ap_webui'].stop()

            # if the ip_addr is provided, it means we set only FM url for one that device so exit the function
            if kwa.has_key('ip_addr'): return

        if not found_ap:
            self.errmsg += '\nCannot find ip address "%s" in the tested devices'

        # print '-----------Finish: _setApFmUrl-------------'


    def _testAPCfgs(self, **kwa):
        '''
        This function is to make sure configuration of APs is auto configured correctly.
        If the ip_addr is provied in kwa, it only check for that ip (stressTest). Otherwise, check all test devices.

        kwa:
        - ip_addr: for stress test only
        - options: for stress test only
        '''

        logging.info('--------------Start: _testAPCfgs--------------')
        #logging.info('Test the AP Provisioned Config for model %s' % self.p['model'])
        self.errmsg = ''
        #new_aps = self._createNewAPsIfHasNewUserAndPassword()
        #tested_aps = new_aps if new_aps != None else self.aps

        # Remove un-neccessary items in wlan detail before doing compare before FM and AP config
        # In the future will add better code to remove all nesscessa
        logging.info('Add/Remove items before doing compare')
        provisioned_options = kwa['options'] if kwa.has_key('options') else self.p['options']

        filter_cfg_options = self._add_removeSometemsForComparison(**provisioned_options)

        found_ap = False
        try:
            for ap in self.test_aps:
            #logging.info('Testing for AP : %s' % ap['config'])
                if kwa.has_key('ip_addr') and ap['ip_addr'] != kwa['ip_addr']:
                    continue

                logging.info('Test the AP Provisioned Config for AP %s' % ap['ip_addr'])

                found_ap = True
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

                ap['ap_webui'].start(5)
                #tmp = ap._tmp_[self.timestamp]
                for k,v in filter_cfg_options.iteritems():
                    if v != None:
                        ap_info = ap_map_func[k](**v) # Base on items of v to get those info from ap
                        msg = self._compareTwoDicts(**{'FM':v, 'AP':ap_info})
                        if msg != '' :
                            self.errmsg += k + ': ' + msg + '\n'
                        del ap_info

                    # After comparing all configured items of ex_options, if there is no error message in
                    # errmsg => The second auto config rule is applied for test APs => Error
                ap['ap_webui'].stop()
                # if ip_addr provided, it means we verify only one AP
                if self.errmsg != '' or kwa.has_key('ip_addr'): break

        except Exception, e:
            self.errmsg += str(e)
            log_trace()

        if not found_ap:
            self.errmsg += '\nCannot find ip address "%s" in the tested devices'
            logging.info(self.errmsg)

        if self.errmsg == '':
            logging.info('All APs auto configured successfully')
        else:
            logging.info('ERROR: %s' % self.errmsg)

        logging.info('---------------Finish: _testAPCfgs---------------')


    def _doVerifyStopAutoCfgRuleTest(self):
        '''
        This function is to verify status of the auto config rule after stopping it to make sure
        it stopped correctly
        '''
        a = self.aliases
        cancel_status = ['cancelled', 'canceled']

        logging.info('Verifying status of the auto config rule %s' % self.p['cfg_rule_name'])
        try:
            status = a.fm.get_auto_cfg_rule_status(cfg_rule_name=self.p['cfg_rule_name'])
            if status.lower() in cancel_status:
                logging.info('The rule %s has been stopped correctly' % self.p['cfg_rule_name'])
            else:
                logging.info('It is expected the rule stopped but it reports as %s' % status)
        except Exception, e:
            self.errmsg = "ERROR: %s" % e
            log_trace()

        if self.errmsg !='': logging.info(self.errmsg)


    def _doVerifyRestartAutoCfgRuleTest(self):
        '''
        This function is to verify status of the auto config rule after restart it to make sure
        it can be restarted correctly
        '''
        a = self.aliases
        running_status = ['running']

        logging.info('Verifying status of the auto config rule %s' % self.p['cfg_rule_name'])
        try:
            status = a.fm.get_auto_cfg_rule_status(cfg_rule_name=self.p['cfg_rule_name'])
            if status.lower() in running_status:
                logging.info('The rule %s has been restarted correctly' % self.p['cfg_rule_name'])
            else:
                logging.info('It is expected the rule running but it reports as %s' % status)
        except Exception, e:
            self.errmsg = "ERROR: %s" % e
            log_trace()

        if self.errmsg !='': logging.info(self.errmsg)


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
            'validateInputData': {
                'initTest': self._initValidateInputDataTest,
                'executeMainJob': self._doValidateInputDataTest,
                'followUpTask': None,
                'testTheResults': None,
                'restoreCfg': self._doRestoreForValidateInputDataTest,
            },
            'stressTest': {
                'initTest': self._initStressTest,
                'executeMainJob': self._doStressTest,
                'followUpTask': None,
                'testTheResults': None,
                'restoreCfg': self._doRestoreForStressTest,
            },
            # This test is for stopping auto config rule testing
            'stop_auto_cfg_rule': {
                'initTest': self._initNormalTest,
                'executeMainJob': self._doStopAutoCfgRuleTest,
                'followUpTask': None,
                'testTheResults': self._doVerifyStopAutoCfgRuleTest,
                'restoreCfg': None,
            },
            # This test is for stopping auto config rule testing
            'restart_auto_cfg_rule': {
                'initTest': self._initNormalTest,
                'executeMainJob': self._doRestartAutoCfgRuleTest,
                'followUpTask': None,
                'testTheResults': self._doVerifyRestartAutoCfgRuleTest,
                'restoreCfg': self._doRestoreForRestartAutoCfgRuleTest,
            },
        }[kwa['test_type']]


