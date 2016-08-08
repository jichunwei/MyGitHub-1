"""
Re-write later
Description: FM_CreateTemplates test class tests the ability of FM to create a new configuration template for
             models such as 2925, 2942, and 7942.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1.
   Required components: FlexMaster
   Test parameters:
       'template_model': 'Model to create a template'.
       'internet': {
            'gateway': "An invalid value to do invalid check: enter an IP like '1.1.1, 1.1.1.-2, 256.1.1.3'",
            'conn_type': '"static" to do invalid check for IP address'
            'ip_addr': "An invalid IP to do the check: 1.1.1.-1, 1.1.1, 256.1.1.1",
            'mask': "List of invalid mask to do the check: 255.255.255.256, 255.255.0, -55.255.255.0",
       },
       'wlan_#{num}': {
            # num is a number from 1 to 8 for eight wireles lan
            'wlan_num': "A number  to point out wlan 1 -> wlan 8",
            'dtim': 'A number out of range (1, 255) to do the check',
            'frag_threshold': 'A number out of range (245, 2346) to do the check',
            'rtscts_threshold': 'A number out of range (245, 2346) to do the check',
       },
       'mgmt': {
            'telnet_port': "A number out of valid range (1,65535) for the port",
            'ssh_port': "A number out of valid range (1,65535) for the port",
            'http_port': "A number out of valid range (1,65535) for the port",
            'https_port': "A number out of valid range (1,65535) for the port",
            'log_srv_ip': "An invalid ip to do the check (1-65535)",
            'log_srv_port': "A number out of valid range (1,65535) for the port",
        },
       'vlan': {
            'mgmt_id': "An invalid number out of valid range (1, 4094) to do the check",
            'tunel_id': "An invalid number out of valid range (1, 4094) to do the check",
            'vlan_a_id': "An invalid number out of valid range (1, 4094) to do the check",
            'vlan_b_id': "An invalid number out of valid range (1, 4094) to do the check",
            'vlan_c_id': "An invalid number out of valid range (1, 4094) to do the check",
            'vlan_d_id': "An invalid number out of valid range (1, 4094) to do the check",
            'vlan_e_id': "An invalid number out of valid range (1, 4094) to do the check",
            'vlan_f_id': "An invalid number out of valid range (1, 4094) to do the check",
            'vlan_g_id': "An invalid number out of valid range (1, 4094) to do the check",
            'vlan_h_id': "An invalid number out of valid range (1, 4094) to do the check",
       }

   Result type: PASS/FAIL/ERROR
   Results: PASS: if the template can check all invalid values.
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

class FM_CheckValidationConfTemplate(Test):
    required_components = ['FM']
    parameter_description = {
        'template_model':   'required; ',
        'internet': 'required; a dictionary contains items to do invalid check for Internet option configuration',
        'wlan_#{num}': 'required; a dictionary contains items to do invalid check for WLAN 1 to WLAN 8 option configuration',
        'mgmt': 'required; a dictionary contains items to do invalid check for Management option configuration',
        'vlan': 'required; a dictionary contains items to do invalid check for VLAN option configuration',
    }

    def config(self, conf):
        self._cfgInitCommonVariables()
        self._cfgInitTestParams(conf)


    def test(self):

        self._check_validation_cfg_template_values()
        if self.errmsg:
            logging.info('Returned error message for doing check invalid values: %s' % (self.errmsg))
            return ('FAIL', self.errmsg)

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

        logging.info('Information for the test:')

        if conf.has_key('template_model'):
            self.template_model = map_template_model[conf['template_model'].upper()]
        else:
            # Get the default wlan configuration if the parameter 'wlan_cfg' is not passed.
            logging.info('Use a default template model for this test')
            self.template_model = map_template_model['ZF2925']

        logging.info('Template model: %s' % self.template_model)

        # Use title of this option as a key
        conf_opt_map = {
            #Its format likes: 'key': [tiltle_of_conf_option, detail_items_for_the_conf]
            'internet': [self.cfm['PRO_INTERNET_TITLE'], conf['internet']if conf.has_key('internet') else None],
            'mgmt'    : [self.cfm['PRO_MGMT_TITLE'],     conf['mgmt']if conf.has_key('mgmt') else None],
            'wlan_1'  : [self.cfm['PRO_WLAN_1_TITLE'],   conf['wlan_1']if conf.has_key('wlan_1') else None],
            'wlan_2'  : [self.cfm['PRO_WLAN_2_TITLE'],   conf['wlan_2']if conf.has_key('wlan_2') else None],
            'wlan_3'  : [self.cfm['PRO_WLAN_3_TITLE'],   conf['wlan_3']if conf.has_key('wlan_3') else None],
            'wlan_4'  : [self.cfm['PRO_WLAN_4_TITLE'],   conf['wlan_4']if conf.has_key('wlan_4') else None],
            'wlan_5'  : [self.cfm['PRO_WLAN_5_TITLE'],   conf['wlan_5']if conf.has_key('wlan_5') else None],
            'wlan_6'  : [self.cfm['PRO_WLAN_6_TITLE'],   conf['wlan_6']if conf.has_key('wlan_6') else None],
            'wlan_7'  : [self.cfm['PRO_WLAN_7_TITLE'],   conf['wlan_7']if conf.has_key('wlan_7') else None],
            'wlan_8'  : [self.cfm['PRO_WLAN_8_TITLE'],   conf['wlan_8']if conf.has_key('wlan_8') else None],
            'vlan'    : [self.cfm['PRO_VLAN_TITLE'],     conf['vlan']if conf.has_key('vlan') else None],
        }

        #print "CONFIGURATION: %s" % conf_opt_map
        item = 'internet'
        self.list_conf_options[conf_opt_map[item][0]] = conf_opt_map[item][1] if conf.has_key(item) else None
        logging.info('Items for "%s": %s' % (conf_opt_map[item][0], self.list_conf_options[conf_opt_map[item][0]]))

        item = 'mgmt'
        self.list_conf_options[conf_opt_map[item][0]] = conf_opt_map[item][1] if conf.has_key(item) else None
        logging.info('Items for "%s": %s' % (conf_opt_map[item][0], self.list_conf_options[conf_opt_map[item][0]]))

        item = 'vlan'
        self.list_conf_options[conf_opt_map[item][0]] = conf_opt_map[item][1] if conf.has_key(item) else None
        logging.info('Items for "%s": %s' % (conf_opt_map[item][0], self.list_conf_options[conf_opt_map[item][0]]))


        # Get items for wlan 1 to wlan 8
        for i in range(1,9):
            item = 'wlan_%d' % i
            self.list_conf_options[conf_opt_map[item][0]] = conf_opt_map[item][1] if conf.has_key(item) else None
            logging.info('Items for "%s": %s' % (conf_opt_map[item][0], self.list_conf_options[conf_opt_map[item][0]]))


        # Check to make sure that there is at least one configuration option provided its sub-items
        for k in self.list_conf_options.iterkeys():
            if self.list_conf_options[k] != None:
                no_provided_option = False

        if no_provided_option:
            raise Exception('No configuration option provided, cannot start the test case')

        logging.info('---------Finish: _cfgInitTestParams---------')


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

    def _check_validation_cfg_template_values(self):
        logging.info('---------Start: _check_validation_cfg_template_values---------')
        self.errmsg = None
        # Create a new template with configurations provided in list_conf_options
        try:
            self.errmsg = self.fm.check_validation_cfg_template_values(template_model=self.template_model, options=self.list_conf_options)
        except Exception:
            self.errmsg = 'An error happens while do check invalid value for Configuration Template. %s' % \
                          (traceback.format_exc())
            logging.info(self.errmsg)

        logging.info('---------Finish: _check_validation_cfg_template_values---------')

