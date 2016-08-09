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


class FM_DeleteConfTemplate(Test):
    required_components = ['FM']
    parameter_description = {
        'template_name':  'required; the name of the template to delete',
    }

    def config(self, conf):
        self._cfgInitCommonVariables()
        self._cfgInitTestParams(conf)
        self._cfgCreateNewTemplateIfNotExist(conf)

    def test(self):

        time.sleep(3)
        self._testDeleteConfTemplate()
        if self.errmsg:
            logging.info('=============FAIL===============')
            return ('FAIL', self.errmsg)

        self._searchTheDeletedTemplate()
        if self.errmsg:
            logging.info('=============FAIL===============')
            return ('FAIL', self.errmsg)

        logging.info('=============PASS===============')
        return ('PASS','')


    def cleanup(self):
        """
        """
        # log out all APs and FM
        logging.info('Cleaning up variables created for this %s' % self.tc_name)

        logging.info('Execution Total Time for %s = %s' \
              % (self.tc_name, time.time() - self.start_time))

        self.fm.logout()


    def _cfgInitTestParams(self, conf):

        logging.info('---------Start: _cfgInitTestParams---------')

        self.tc_name = self.__class__.__name__
        logging.info('--------Start configuring for %s test case--------' % self.tc_name)
        self.start_time = time.time()

        logging.info('Information for the template:')

        if not conf.has_key('template_name') or len(conf['template_name'])==0 :
            self.template_name = 'Test_Delete_template' #+ get_random_string('ascii',3,10)
        else:
            self.template_name = conf['template_name']


        logging.info('Template name: %s' % self.template_name)

        logging.info('---------Finish: _cfgInitTestParams---------')


    def _cfgCreateNewTemplateIfNotExist(self, conf):
        logging.info('---------Start: _cfgCreateANewTemplateIfNotExist---------')
        # If this template doesn't exist, create a new one
        list_conf_options = {}
        #no_provided_option = True

        if None== self.fm.search_cfg_template(self.template_name):
            map_template_model = {
                               'ZF2925' :"Ruckus ZF2925 Device", # For 2925 template
                               'ZF2942' :"Ruckus ZF2942 Device", # For 2942 template
                               'ZF7942' :"Ruckus ZF7942 Device" # For 7942 template
                                #"Management Server Configuration" # For "ACS" template
            }

            if conf.has_key('template_model'):
                self.template_model = map_template_model[conf['template_model'].upper()]
            else:
                # Get the default wlan configuration if the parameter 'wlan_cfg' is not passed.
                logging.info('Not found template model so using the default template model ZF2925 for this test')
                self.template_model = map_template_model['ZF2925']

            logging.info('Template model: %s' % self.template_model)

            # Use title of this option as a key
            conf_opt_map = {
                #Its format likes: 'key': [tiltle_of_conf_option, detail_items_for_the_conf]
                'device_general': [self.cfm['PRO_DEV_GENERAL_TITLE'], conf['device_general']if conf.has_key('device_general') else None],
                'wlan_common'   : [self.cfm['PRO_WLAN_COMMON_TITLE'], conf['wlan_common']if conf.has_key('wlan_common') else None],
                'wlan_1'        : [self.cfm['PRO_WLAN_1_TITLE'],      conf['wlan_1']if conf.has_key('wlan_1') else None],
                'wlan_2'        : [self.cfm['PRO_WLAN_2_TITLE'],      conf['wlan_2']if conf.has_key('wlan_2') else None],
                'wlan_3'        : [self.cfm['PRO_WLAN_3_TITLE'],      conf['wlan_3']if conf.has_key('wlan_3') else None],
                'wlan_4'        : [self.cfm['PRO_WLAN_4_TITLE'],      conf['wlan_4']if conf.has_key('wlan_4') else None],
                'wlan_5'        : [self.cfm['PRO_WLAN_5_TITLE'],      conf['wlan_5']if conf.has_key('wlan_5') else None],
                'wlan_6'        : [self.cfm['PRO_WLAN_6_TITLE'],      conf['wlan_6']if conf.has_key('wlan_6') else None],
                'wlan_7'        : [self.cfm['PRO_WLAN_7_TITLE'],      conf['wlan_7']if conf.has_key('wlan_7') else None],
                'wlan_8'        : [self.cfm['PRO_WLAN_8_TITLE'],      conf['wlan_8']if conf.has_key('wlan_8') else None],
            }

            #print "CONFIGURATION: %s" % conf_opt_map

            item = 'device_general'
            list_conf_options[conf_opt_map[item][0]] = conf_opt_map[item][1] if conf.has_key(item) else None
            logging.info('Items for Device General: %s' % list_conf_options[conf_opt_map[item][0]])

            item = 'wlan_common'
            list_conf_options[conf_opt_map[item][0]] = conf_opt_map[item][1] if conf.has_key(item) else None
            logging.info('Items for Wireless Common: %s' % list_conf_options[conf_opt_map[item][0]])

            # Get items for wlan 1 to wlan 8
            for i in range(1,9):
                item = 'wlan_%d' % i
                list_conf_options[conf_opt_map[item][0]] = conf_opt_map[item][1] if conf.has_key(item) else None
                logging.info('Items for Wireless %d: %s' % (i, list_conf_options[conf_opt_map[item][0]]))

            try:
                self.fm.create_cfg_template(template_name=self.template_name, template_model=self.template_model, options=list_conf_options)
                #logging.info('Detail information for "%s": "%s"' % (key, conf_option[key]))
            except Exception:
                raise ('Cannot create a new template to start this test. Reason: %s' % traceback.format_exc())

        logging.info('---------Finish: _cfgCreateANewTemplateIfNotExist---------')


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
        try:
            self.fm.delete_cfg_template_by_name(self.template_name)
            logging.info('Deleted tempalte "%s" successfully' % (self.template_name))

        except Exception:
            self.errmsg = 'Fail to delete template "%s". Reason: %s' % \
                          (self.template_name, traceback.format_exc())
            logging.info(self.errmsg)

        logging.info('---------Finish: _testDeleteConfTemplate---------')


    def _searchTheDeletedTemplate(self):
        logging.info('---------Start: _searchTheDeletedTemplate---------')
        self.errmsg = None
        try:
            # search the deleted template to make sure it was deleted correctly
            if None == self.fm.search_cfg_template(self.template_name):
                logging.info('Not found the template "%s", it was deleted correctly' % (self.template_name))
            else:
                self.errmsg = 'The template "%s" was deleted but somehow it is stil there' % self.template_name
                logging.info(self.errmsg)

        except Exception:
            self.errmsg = 'Unexpected errors happens while searching the deleted template "%s". Reason: %s' % \
                          (self.template_name, traceback.format_exc())
            logging.info(self.errmsg)

        logging.info('---------Finish: _searchTheDeletedTemplate---------')

