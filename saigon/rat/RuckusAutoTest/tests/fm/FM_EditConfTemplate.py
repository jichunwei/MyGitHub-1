"""
Re-write later
Description: FM_CreateTemplates test class tests the ability of FM to create a new configuration template for
             models such as 2925, 2942, and 7942.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1.
   Required components: FlexMaster
   Test parameters: 'template_model': 'Model to create a template'.
                         EX: It must follow below values for the model.
                            "Ruckus ZF2925 Device": For 2925 template
                            "Ruckus ZF2942 Device": For 2942 template
                            "Ruckus VF2825 Device (ruckus01)": For 2825 ruckus profile 1 template
                            "Ruckus VF2825 Device (ruckus03)": For 2825 ruckus profile 3 template
                            "Ruckus VF2825 Device (ruckus04)": For 2825 ruckus profile 4 template
                            "Ruckus VF7811 Device": For 7811 template
                            "Ruckus ZF7942 Device": For 7942 template
                            "Ruckus VF2811 Device": For 2811 template
                            "Management Server Configuration": For "ACS" template

                    #Optional key. If don't provide belows keys the test class will generate them randomly.
                    'template_name': 'name of template 1',

                    'old_confs': # a dictionary contains items to create a template with these configurations.
                                 # It has the following items
                    {
                        'device_general': 'refer to FM_CreateConfTemp to know this item',
                        'wlan_common': 'refer to FM_CreateConfTemp to know this item',
                        'wlan_#{num}': 'refer to FM_CreateConfTemp to know this item',
                    }
                    'old_confs': # a dictionary contains items to edit a template, which has just beend created with the old_confs, with these configurations.
                                 # It has the following items
                    {
                        'device_general': 'refer to FM_CreateConfTemp to know this item',
                        'wlan_common': 'refer to FM_CreateConfTemp to know this item',
                        'wlan_#{num}': 'refer to FM_CreateConfTemp to know this item',
                    }

   Result type: PASS/FAIL/ERROR
   Results: PASS: if configuration template(s) are created successfully with provided configuration.
            FAIL: if one of the above criteria is not satisfied
            ERROR: if some unexpected events happen

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - If users provide information for the test, get it. Otherwise, generate it.
   2. Test:
       - For each provided information of a template, create a new template respectively
       - After creating new templates successfully, verify to make sure them containing the provided info exactlys
   3. Cleanup:
"""

import os, time, logging, re, random, traceback
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.common.Ratutils import *
from RuckusAutoTest.common.DialogHandler import *

class FM_EditConfTemplate(Test):
    required_components = ['FM']
    parameter_description = {
        'template_model':   'required; the model of AP: ZF2925, ZF2942 or ZF7942',
        'template_name':  'optional; the name of the template',
        'device_general': 'required; a dictionary contains items for Device General option configuration',
    }

    def config(self, conf):
        self._cfgInitCommonVariables()
        self._cfgInitTestParams(conf)
        self._cfgDeleteTheTemplate()


    def test(self):

        self._testEditConfTemplate()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testVerifyEditedConfTemplate()
        if self.errmsg: return ('FAIL', self.errmsg)
        return ('PASS','')


    def cleanup(self):
        """
        """
        # log out all APs and FM
        logging.info('Cleaning up variables created for this %s' % self.tc_name)

        self._cleanupDeleteCreatedTemplate()

        logging.info('Execution Total Time for %s = %s' \
              % (self.tc_name, time.time() - self.start_time))

        self.fm.logout()


    def _cfgInitTestParams(self, conf):

        logging.info('---------Start: _cfgInitTestParams---------')

        self.tc_name = self.__class__.__name__
        logging.info('--------Start configuring for %s test case--------' % self.tc_name)
        self.start_time = time.time()
        self.TASK_SLEEP = 1.5
        #List of configuration options to configure
        self.list_conf_options = {}
        no_provided_option = True

        map_template_model = {
                               'ZF2925' :"Ruckus ZF2925 Device", # For 2925 template
                               'ZF2942' :"Ruckus ZF2942 Device", # For 2942 template
                               'ZF7942' :"Ruckus ZF7942 Device" # For 7942 template
                                #"Management Server Configuration" # For "ACS" template
                             }

        logging.info('Information for the template:')

        if conf.has_key('template_model'):
            self.template_model = map_template_model[conf['template_model'].upper()]
        else:
            # Get the default wlan configuration if the parameter 'wlan_cfg' is not passed.
            logging.info('Use a default template model for this test')
            self.template_model = map_template_model['ZF2925']

        logging.info('Template model: %s' % self.template_model)

        if conf.has_key('template_name'):
            self.template_name = conf['template_name']
        else:
            self.template_name = 'Test for ' + conf['template_model'] # + '_test_template_' + get_random_string('ascii',3,10)

        logging.info('template_name: %s' % self.template_name)

        # Use title of this option as a key
        conf_opt_map = {
            #Its format likes: 'key': [tiltle_of_conf_option, detail_items_for_the_conf]
            'device_general': [self.cfm['PRO_DEV_GENERAL_TITLE'], conf['old_confs']['device_general']if conf['old_confs'].has_key('device_general') else None,  conf['new_confs']['device_general']if conf['new_confs'].has_key('device_general') else None],
            'wlan_common'   : [self.cfm['PRO_WLAN_COMMON_TITLE'], conf['old_confs']['wlan_common']if conf['old_confs'].has_key('wlan_common') else None,        conf['new_confs']['wlan_common']if conf['new_confs'].has_key('wlan_common') else None],
            'wlan_1'        : [self.cfm['PRO_WLAN_1_TITLE'],      conf['old_confs']['wlan_1']if conf['old_confs'].has_key('wlan_1') else None,                  conf['new_confs']['wlan_1']if conf['new_confs'].has_key('wlan_1') else None],
            'wlan_2'        : [self.cfm['PRO_WLAN_2_TITLE'],      conf['old_confs']['wlan_2']if conf['old_confs'].has_key('wlan_2') else None,                  conf['new_confs']['wlan_2']if conf['new_confs'].has_key('wlan_2') else None],
            'wlan_3'        : [self.cfm['PRO_WLAN_3_TITLE'],      conf['old_confs']['wlan_3']if conf['old_confs'].has_key('wlan_3') else None,                  conf['new_confs']['wlan_3']if conf['new_confs'].has_key('wlan_3') else None],
            'wlan_4'        : [self.cfm['PRO_WLAN_4_TITLE'],      conf['old_confs']['wlan_4']if conf['old_confs'].has_key('wlan_4') else None,                  conf['new_confs']['wlan_4']if conf['new_confs'].has_key('wlan_4') else None],
            'wlan_5'        : [self.cfm['PRO_WLAN_5_TITLE'],      conf['old_confs']['wlan_5']if conf['old_confs'].has_key('wlan_5') else None,                  conf['new_confs']['wlan_5']if conf['new_confs'].has_key('wlan_5') else None],
            'wlan_6'        : [self.cfm['PRO_WLAN_6_TITLE'],      conf['old_confs']['wlan_6']if conf['old_confs'].has_key('wlan_6') else None,                  conf['new_confs']['wlan_6']if conf['new_confs'].has_key('wlan_6') else None],
            'wlan_7'        : [self.cfm['PRO_WLAN_7_TITLE'],      conf['old_confs']['wlan_7']if conf['old_confs'].has_key('wlan_7') else None,                  conf['new_confs']['wlan_7']if conf['new_confs'].has_key('wlan_7') else None],
            'wlan_8'        : [self.cfm['PRO_WLAN_8_TITLE'],      conf['old_confs']['wlan_8']if conf['old_confs'].has_key('wlan_8') else None,                  conf['new_confs']['wlan_8']if conf['new_confs'].has_key('wlan_8') else None],
        }

        #print "CONFIGURATION: %s" % conf_opt_map

        self.old_confs = {}
        self.new_confs = {}

        item = 'device_general'
        self.old_confs[conf_opt_map[item][0]] = conf_opt_map[item][1] if conf['old_confs'].has_key(item) else None
        self.new_confs[conf_opt_map[item][0]] = conf_opt_map[item][2] if conf['new_confs'].has_key(item) else None

        #print "OLD CONF: %s" % self.old_confs
        #print "NEW CONF: %s" % self.new_confs

        item = 'wlan_common'
        self.old_confs[conf_opt_map[item][0]] = conf_opt_map[item][1] if conf['old_confs'].has_key(item) else None
        self.new_confs[conf_opt_map[item][0]] = conf_opt_map[item][2] if conf['new_confs'].has_key(item) else None

        # Get items for wlan 1 to wlan 8
        for i in range(1,9):
            item = 'wlan_%d' % i
            self.old_confs[conf_opt_map[item][0]] = conf_opt_map[item][1] if conf['old_confs'].has_key(item) else None
            self.new_confs[conf_opt_map[item][0]] = conf_opt_map[item][2] if conf['new_confs'].has_key(item) else None

        logging.info('Configuration for the test: %s' % conf)

        # Check to make sure that there is at least one configuration option provided its sub-items
        for k in self.old_confs.iterkeys():
            if self.old_confs[k] != None:
                no_provided_option = False

        for k in self.new_confs.iterkeys():
            if self.new_confs[k] != None:
                no_provided_option = False

        if no_provided_option:
            raise Exception('No configuration option provided for either old_confs or new_confs. Cannot start the test case')

        logging.info('---------Finish: _cfgInitTestParams---------')


    def _cfgDeleteTheTemplate(self):

        logging.info('---------Start: _cfgDeleteTheTemplate---------')

        try:
            logging.info('Delete the template %s if exist' % self.template_name)
            self.fm.delete_cfg_template_by_name(self.template_name)
        except Exception:
            pass

        logging.info('---------Finish: _cfgDeleteTheTemplate---------')


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

    def _testEditConfTemplate(self):
        logging.info('---------Start: _testEditConfTemplate---------')
        self.errmsg = None
        # Create a new template with configurations provided in list_conf_options
        try:
            # Before editing create a new one
            self.fm.create_cfg_template(template_name=self.template_name, template_model=self.template_model, options=self.old_confs)
            logging.info('Created tempalte "%s" for model "%s" successfully' %\
                         (self.template_name, self.template_model))

            self.fm.edit_cfg_template(template_name=self.template_name, template_model=self.template_model, old_confs=self.old_confs, new_confs=self.new_confs)
            logging.info('Edited tempalte "%s" for model "%s"' %\
                         (self.template_name, self.template_model))

        except Exception:
            self.errmsg = 'Have error while editing template with name: "%s", template model: "%s". Reason: %s' % \
                          (self.template_name, self.template_model, traceback.format_exc())
            logging.info(self.errmsg)

        logging.info('---------Finish: _testEditConfTemplate---------')


    def _testVerifyEditedConfTemplate(self):
        logging.info('---------Start: _testVerifyEditedConfTemplate---------')
        self.errmsg = None
        # Create a new template with configurations provided in list_conf_options
        try:
            self.fm.verify_cfg_template(template_name=self.template_name, template_model=self.template_model, options=self.new_confs)
            logging.info('The tempalte "%s" for model "%s" is edited successfully as provided configurations' %\
                         (self.template_name, self.template_model))

        except Exception:
            self.errmsg = 'The new template "%s" have some differences with the provided configuration: %s. Reason: %s' % \
                          (self.template_name, self.new_confs, traceback.format_exc())
            logging.info(self.errmsg)

        logging.info('---------Finish: _testVerifyEditedConfTemplate---------')


    def _cleanupDeleteCreatedTemplate(self):
        logging.info('---------Start: _cleanupDeleteCreatedTemplate---------')

        try:
            #self.fm.delete_all_cfg_template()
            logging.info('Delete the template %s if exist' % self.template_name)
            self.fm.delete_cfg_template_by_name(self.template_name)
        except Exception:
            pass

        logging.info('---------Finish: _cleanupDeleteCreatedTemplate---------')
