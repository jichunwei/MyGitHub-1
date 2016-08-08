"""
Re-write later
Description: FM_CreateTemplates test class tests the ability of FM to create a new configuration template for
             models such as 2925, 2942, and 7942.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1.
   Required components: FlexMaster
   Test parameters:
                    'template_name': 'name of template to delete'
                        Note: If no template_name provided or the provided template doesn't exist,
                        the script will create a new template with simple configuration to do test.

   Result type: PASS/FAIL/ERROR
   Results: PASS: if the template can be deleted successfully.
            FAIL: if one of the above criteria is not satisfied
            ERROR: if some unexpected events happen

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - Init essential parameters.
       - Init common variable for the test.
       - Create a template with simple configuration if the provided template doesn't exist.

   2. Test:
       - Delete the template
       - Search the template to make sure that it is deleted correctly.
   3. Cleanup:
"""

import time
import logging
import traceback

from RuckusAutoTest.models import Test
from RuckusAutoTest.common.utils import get_timestamp


class FM_DeleteAutoConfTemplate(Test):
    required_components = ['FM']
    parameter_description = {
        'template_model': 'required; specify the model',
        'options': 'required; configuration options for the template',
        'template_name': 'optional; specify name of the template',
        'cfg_rule_name': 'optional; specify name of the auto cfg rule',
        'device_group': 'optional; use "All Standalone APs" by default',

    }

    def config(self, conf):
        self._cfgInitCommonVariables()
        self._cfgInitTestParams(conf)

    def test(self):
        self.errmsg = None

        self._createNewTemplate()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._create_auto_cfg_rule()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testDeleteConfTemplate()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._searchTheDeletedTemplate()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS','')


    def cleanup(self):
        """
        """
        # log out all APs and FM
        logging.info('Cleaning up variables created for this %s' % self.tc_name)
        self._stop_auto_cfg_rule()
        logging.info('Execution Total Time for %s = %s' \
              % (self.tc_name, time.time() - self.start_time))

        self.fm.logout()


    def _cfgInitTestParams(self, conf):
        '''
        Init parameters for the test. Init following params:
            'template_model': 'required; specify the model',
            'options': 'required; configuration options for the template',
            'template_name': 'optional; specify name of the template',
            'cfg_rule_name': 'optional; specify name of the auto cfg rule',
            'device_group': 'optional; use "All Standalone APs" by default',
        '''
        logging.info('---------Start: _cfgInitTestParams---------')

        self.tc_name = self.__class__.__name__
        logging.info('Start configuring for %s test case' % self.tc_name)
        self.start_time = time.time()

        self.timestamp = get_timestamp()

        logging.info('Information for this:')
        self.template_model = conf['template_model'] if conf.has_key('template_model') else 'ZF2925'
        self.options = conf['options'] if conf.has_key('options') else {'device_general': {'device_name': 'RuckusAPTest'}}
        self.template_name = 'AutoCfgTemplate' +'_' + conf['template_model'] + '_' + self.timestamp
        self.cfg_rule_name = 'AutoCfgRule' +'_' + conf['template_model'] + '_' + self.timestamp
        self.device_group = conf['device_group'] if conf.has_key('device_group') else "All Standalone APs"

        logging.info('\tTemplate name: %s\n'\
                      '\tTemplate model: %s\n'\
                      '\tConfig rule: %s\n'\
                      '\tDevice group: %s\n'\
                      '\tConfig options: %s\n' %\
                      (self.template_name, self.template_model,
                      self.cfg_rule_name, self.device_group, self.options))

        logging.info('---------Finish: _cfgInitTestParams---------')


    def _createNewTemplate(self):
        logging.info('---------Start: _createNewTemplateIfNotExist---------')
        try:
            self.fm.create_cfg_template(template_name=self.template_name, template_model=self.template_model, \
                                       options=self.options, convert_in_advanced=True)
            #logging.info('Detail information for "%s": "%s"' % (key, conf_option[key]))
        except Exception:
            raise ('Cannot create a new template to start this test. Reason: %s' % traceback.format_exc())

        logging.info('---------Finish: _createNewTemplateIfNotExist---------')


    def _create_auto_cfg_rule(self):
        '''
        Create an auto configuration rule for this group
        '''
        # print '-------------Start: _cfgAutoCfgRule-------------'
        #a = self.aliases
        self.errmsg = None
        logging.info('Configure an Auto Config Rule for model %s' % self.template_model)
        try:
            cfg = {
                    'cfg_rule_name': self.cfg_rule_name,
                    'device_group': self.device_group,
                    'model': self.template_model.upper(),
                    'cfg_template_name': self.template_name,
                }
            self.fm.create_auto_cfg_rule(**cfg)
            logging.info('Created an auto config rule "%s" for the test' % self.cfg_rule_name)
        except Exception, e:
            self.errmsg = e.__str__()
            logging.info(self.errmsg)

        # print '-------------Finish: _cfgAutoCfgRule-------------'

    def _stop_auto_cfg_rule(self):
        '''
        To stop an auto cfg rule
        '''
        self.errmsg = None
        try:
            logging.info('Trying to stop the rule %s' % self.cfg_rule_name)
            cfg_rule = self.cfg_rule_name
            self.fm.stop_auto_cfg_rule(cfg_rule_name=cfg_rule)
        except Exception, e:
            self.errmsg = 'BE CAREFUL: Cannot stop the rule %s. It may affect to other test. Error: %s' % (cfg_rule, e.__str__())
            logging.info(self.errmsg)


    def _cfgInitCommonVariables(self):
        #logging.info('Start verifying %s test case' % self.tc_name)
        logging.info('---------Start: _cfgInitCommonVariables---------')

        self.tb  = self.testbed
        self.sm  = self.tb.selenium_mgr
        self.fm  = self.tb.components['FM']
        #self.aps = self.tb.components['APs']
        self.sfm = self.fm.selenium # selenium of FlexMaster

        self.lfm = self.fm.resource['Locators'] # FlexMaster Locators
        self.cfm = self.fm.resource['Constants']
        self.CT = 'ConfTemplates_' # Inventory > Device Firmware pane

        logging.info('---------Finish: _cfgInitCommonVariables---------')


    def _testDeleteConfTemplate(self):
        logging.info('---------Start: _testDeleteConfTemplate---------')
        self.errmsg = None
        # Create a new template with configurations provided in list_conf_options
        exp_msg = 'The template could not be deleted because an auto-configuration task is using it'
        try:
            self.fm.delete_cfg_template_by_name(self.template_name)
            logging.info('Deleted tempalte "%s" successfully' % (self.template_name))
        except Exception, e:
            ret_msg = e.__str__()
            if exp_msg in ret_msg:
                logging.info('Got expected error message: %s' % ret_msg)
            else:
                self.errmsg = 'Fail to delete template "%s". Reason: %s' % \
                          (self.template_name, traceback.format_exc())
                logging.info(self.errmsg)

        logging.info('---------Finish: _testDeleteConfTemplate---------')


    def _searchTheDeletedTemplate(self):
        '''
        It's correct if the template is still there.
        '''
        logging.info('---------Start: _searchTheDeletedTemplate---------')
        self.errmsg = None
        try:
            # search the deleted template to make sure it was deleted correctly
            if None == self.fm.search_cfg_template(self.template_name):
                self.errmsg = 'The template "%s" should not be deleted but it was removed incorrectly' % (self.template_name)
            else:
                logging.info('It is ok. The template "%s" is stil there' % self.template_name)

        except Exception:
            self.errmsg = 'Unexpected errors happens while searching the deleted template "%s". Reason: %s' % \
                          (self.template_name, traceback.format_exc())

        logging.info('---------Finish: _searchTheDeletedTemplate---------')
        if self.errmsg:
            logging.info(self.errmsg)
            raise Exception(self.errmsg)

