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
                    'template_name': 'name of template 1'
                    'device_general': a dictionary, its items may be following things. Note that: it uses the title as a key
                                     {'device_name': 'Name of Device', 'username': 'Name of Super user', 'password': 'Password of Super user', 'cpassword': 'Confirm password'}

                    'wlan_common': {#a dictionary, its items may be following things. Note that: it uses the title as a key
                        'wmode': 'auto, g, b',
                        'channel': 'value from 0 to 11; 0: smartselect, 1: channel 1...',
                        'country_code': 'AU, AT, ...',
                        'txpower': 'max, half, quarter, eighth, min',
                        'prot_mode': 'Disabled, CTS-only, RTS-CTS'
                    }
                    'wlan_{num}': { # wlan_%{num} is "wireless num", {num} should be 1, 2, 3, 4, 5, 6, 7, 8
                        'wlan_num': 'an integer number (from 1 to 8) for wireless 1->8',
                        'avail': 'Disabled, Enabled',
                        'broadcast_ssid': 'Disabled, Enabled',
                        'client_isolation': 'Disabled, Enabled',
                        'wlan_name': 'name of wlan',
                        'wlan_ssid': 'name of ssid',
                        'dtim': 'Data beacon rate (1-255)',
                        'frag_threshold': 'Fragment Threshold (245-2346',
                        'rtscts_threshold': 'RTS / CTS Threshold (245-2346',
                        'rate_limiting': 'Rate limiting: Disabled, Enabled',
                        'downlink': '100kbps, 250kbps, 500kbps, 1mbps, 2mbps, 5mbps, 10mbps, 20mbps, 50mbps',
                        'uplink': '100kbps, 250kbps, 500kbps, 1mbps, 2mbps, 5mbps, 10mbps, 20mbps, 50mbps',

                        #It has error here for Algorithm locators on 7942, temporarily don't use "Disabled"
                        #for encrypt_method on 7942 template to avoid the error. It will be fixed later
                        'encrypt_method': 'Diablded, WEB, WPA',

                        #Detail items for the case "encrypt_method = WEP"
                        'wep_mode': 'Open, SharedKey, Auto',
                        'encryption_len': 'encryption length: 13, 26, 5, 10', #13: 128bit 13 ascii, 26: 128bit 26 hex, 5: 64bit 5 ascii, 10: 64bit 10 hex
                        #Wireless 1 WEP Key Index
                        'wep_key_idx': 'key index: 1, 2, 3, 4',
                        #WEP key password
                        'wep_pass': 'password of wep method',
                        'cwep_pass': ' password of wep method (confirm)',

                        #Detail items for the case "encrypt_method = WPA"
                        #WPA Version
                        'wpa_version': 'WPA version: WPA, WPA2, Auto',
                        #WPA Algorithm:
                        'wpa_algorithm': 'WPA Algorithm: TKIP, AES, Auto',
                        #Authentication
                        'auth': 'Authentication: PSK, 802.1x, Auto',

                        #Detail items for the case "auth = PSK"
                        'psk_passphrase': 'PSK passphrase',
                        'cpsk_passphrase': 'PSK passphrase (confirm)',

                        #Detail items for the case "auth = 802.1x"
                        'radius_nas_id': 'Radius NAS-ID',
                        'auth_ip': 'Authentication IP address',
                        'auth_port': 'Authentication Port',
                        'auth_secret': 'Authentication Server Secret',
                        'cauth_secret': 'Authentication Server Secret',
                        'acct_ip': 'Accounting IP address',
                        'acct_port': 'Accounting Port',
                        'acct_secret': 'Accounting Server Secret',
                        'cacct_secret': 'Accounting Server Secret (confirm)'

                        #Detail items for the case "auth = 802.1x": It includes all items of PSK and 802.1x
                    }


                        Note: If you want to provide your data for this configurations items, you need to enter
                              values for 'device_general' key.
                              To make this easy, please let the test class help generate that information.
                    'internet': 'define later'

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

class FM_CreateConfTemplate(Test):
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

        self._testCreateNewConfTemplate()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testVerifyNewConfTemplate()
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
        self.list_conf_options[conf_opt_map[item][0]] = conf_opt_map[item][1] if conf.has_key(item) else None
        logging.info('Items for Device General: %s' % self.list_conf_options[conf_opt_map[item][0]])

        item = 'wlan_common'
        self.list_conf_options[conf_opt_map[item][0]] = conf_opt_map[item][1] if conf.has_key(item) else None
        logging.info('Items for Wireless Common: %s' % self.list_conf_options[conf_opt_map[item][0]])

        # Get items for wlan 1 to wlan 8
        for i in range(1,9):
            item = 'wlan_%d' % i
            self.list_conf_options[conf_opt_map[item][0]] = conf_opt_map[item][1] if conf.has_key(item) else None
            logging.info('Items for Wireless %d: %s' % (i, self.list_conf_options[conf_opt_map[item][0]]))


        # Check to make sure that there is at least one configuration option provided its sub-items
        for k in self.list_conf_options.iterkeys():
            if self.list_conf_options[k] != None:
                no_provided_option = False

        if no_provided_option:
            raise Exception('No configuration option provided, cannot start the test case')

        logging.info('---------Finish: _cfgInitTestParams---------')


    def _cfgDeleteTheTemplate(self):

        logging.info('---------Start: _cfgDeleteTheTemplate---------')
        try:
            #self.fm.delete_all_cfg_template()
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

    def _testCreateNewConfTemplate(self):
        logging.info('---------Start: _testCreateNewConfTemplate---------')
        self.errmsg = None
        # Create a new template with configurations provided in list_conf_options
        try:
            self.fm.create_cfg_template(template_name=self.template_name, template_model=self.template_model, options=self.list_conf_options)
            logging.info('Created tempalte "%s" for model "%s" successfully' %\
                         (self.template_name, self.template_model))

        except Exception:
            self.errmsg = 'Fail to create template with name: "%s", template model: "%s", Configuration: %s. Reason: %s' % \
                          (self.template_name, self.template_model, self.list_conf_options, traceback.format_exc())
            logging.info(self.errmsg)

        logging.info('---------Finish: _testCreateNewConfTemplate---------')


    def _testVerifyNewConfTemplate(self):
        logging.info('---------Start: _testVerifyNewConfTemplate---------')
        self.errmsg = None
        # Create a new template with configurations provided in list_conf_options
        try:
            self.fm.verify_cfg_template(template_name=self.template_name, template_model=self.template_model, options=self.list_conf_options)
            logging.info('The tempalte "%s" for model "%s" is created successfully as provided configurations' %\
                         (self.template_name, self.template_model))

        except Exception:
            self.errmsg = 'The new template "%s" have some differences with the provided configuration: %s. Reason: %s' % \
                          (self.template_name, self.list_conf_options, traceback.format_exc())
            logging.info(self.errmsg)

        logging.info('---------Finish: _testVerifyNewConfTemplate---------')


    def _cleanupDeleteCreatedTemplate(self):
        logging.info('---------Start: _cleanupDeleteCreatedTemplate---------')

        try:
            logging.info('Delete the created template %s if exist' % self.template_name)
            self.fm.delete_cfg_template_by_name(self.template_name)
        except Exception:
            pass

        logging.info('---------Finish: _cleanupDeleteCreatedTemplate---------')
