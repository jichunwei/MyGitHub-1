# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_AP_Country_Code Test class tests the ability of AP to join the ZD before and after the ZD changes its country code.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector', 'RuckusAP'
   Test parameters: 'locked_ap'   : 'Mac address of the AP with "fixed ctry code" status is set to "yes"
                                    (country code locked AP), called it AP1',
                    'nonlocked_ap': 'Mac address of the AP with "fixed ctry code" status is set to "no"
                                    (non-country code locked AP), called it AP2',
                    'is_ap_join_after_change'   : 'The bool value indicates that whether ZD should change its country code before APs join or not.
                                    If is_ap_join_after_change is False, the ZD changes its country code after APs join
                                    If is_ap_join_after_change is True, the ZD changes its country code before APs join'

   Result type: PASS/FAIL
   Results: PASS: After the ZD changes the country code, the AP2 can discover and join the ZD,
                  get the same country code setting as the one configured in the ZD. The AP1 can not connect to the ZD.
            FAIL: If one of the above criteria is not met.

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - Change "fixed ctry code" status on AP1 is "yes", and "fixed ctry code" status on AP2 is "no"
       - If is_ap_join_after_change is True, remove the tested APs out of the Access Points table
       - Change country code in the ZD
   2. Test procedure:
       - If is_ap_join_after_change is True, navigate to the Monitor/Access Points page, verify that 2 tested APs disappear from
         the AP-Summary table
         If is_ap_join_after_change is False, verify that 2 tested APs are in "Disconnected" status
       - After APs reboot, the AP1 can join the ZD, but the AP2 can not because of the difference of
         country code setting with the ZD
       - The AP2 can be made provision from the ZD successfully and has the same country code setting
         as the configured in the ZD.
       - If is_ap_join_after_change is True, verify that the AP1 can not join the ZD, and there is no entry about it appearing
         in the AP-Summary table
       - If is_ap_join_after_change is False, verify that although AP1's entry is still in the AP-Summary table
         but its status is Disconnected
   3. Cleanup:
       - Return the old country code for the ZD
       - Return the old "fixed ctry code" status for the AP1 and AP2

    How it was tested:
        1. After AP1 reboots and the provision is not made, using console to login to the AP1, change "fixed ctry code"
           status of AP1 to "no". The test script will return FAIL because this AP joins the ZD while it can't.
        2. After AP2 reboots and the provision is not made, using console to login to the AP2, change "fixed ctry code"
           status of AP2 to "yes". The test script will return FAIL because this AP does not join the ZD while it can.
"""

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig

class ZD_AP_Country_Code(Test):
    required_components = ['ZoneDirector', 'RuckusAP']
    parameter_description = {'locked_ap'    : 'Mac address of the country code locked AP (XX:XX:XX:XX:XX:XX)',
                              'nonlocked_ap' : 'Mac address of the non country code locked AP (XX:XX:XX:XX:XX:XX)',
                              'is_ap_join_after_change' : 'This is the bool value used to decide if the ZoneDirector is changed country \
                               code before APs join or not'}
    def config(self, conf):

        self.is_ap_join_after_change = conf['is_ap_join_after_change']
        self.comp = []
        self.mac_list = []
        
        self.old_ctrycode = self.testbed.components['ZoneDirector'].get_country_code()
        self.old_status = self.testbed.components['ZoneDirector'].get_ap_policy_approval()

        self.current_aps_cfg = []
        logging.info("Get current configuration of APs on the ZD")
        aps_info = self.testbed.components['ZoneDirector'].get_all_ap_info()
        for ap in aps_info:
            ap_cfg = self.testbed.components['ZoneDirector'].get_ap_cfg(ap['mac'])
            self.current_aps_cfg.append(ap_cfg)
            time.sleep(1)

        # Get exactly tested components and save them to a list
        # Append mac address of locked AP to the list first
        
        
        if conf.has_key('locked_ap'):
            self.ap = tconfig.get_testbed_active_ap(self.testbed, conf['locked_ap'])
            if self.ap:
                self.comp.append(self.ap)
                self.old_ctrycode_locked = self.ap.get_fixed_country_code()
                self.mac_list.append(self.ap.get_base_mac().lower())
            else:
                raise Exception('Target AP %s not found' % conf['target_ap'])
        
        # After that append mac address of unlocked AP to the list
        if conf.has_key('nonlocked_ap'):
            self.comp_ap = tconfig.get_testbed_active_ap(self.testbed, conf['nonlocked_ap'])
            if self.comp_ap:
                self.comp.append(self.comp_ap)
                self.old_ctrycode_unlocked = self.comp_ap.get_fixed_country_code()
                self.mac_list.append(self.comp_ap.get_base_mac().lower())
            else:
                raise Exception('Target AP %s not found' % conf['target_ap'])
        
        # Change the fixed country code status for APs
        logging.info("Change the \"fixed ctry code\" status of the AP %s to \"yes\"" % self.mac_list[0])
        if self.old_ctrycode_locked.lower() == "no":
            self.comp[0].set_fixed_country_code()

        logging.info("Change the \"fixed ctry code\" status of the AP %s to \"no\"" % self.mac_list[1])
        if self.old_ctrycode_unlocked.lower() == "yes":
            self.comp[1].set_fixed_country_code(False)
            
        #@author: Tan shixiong @bug: zf-13925  
        # If ZD changes country code before APs join, remove all APs out of the Access Points table
        if self.is_ap_join_after_change:
            #disable approval police
            self.testbed.components['ZoneDirector'].set_ap_policy_approval(False) 
            time.sleep(2)
            logging.info("Change country code on the ZoneDirector")
            self.testbed.components['ZoneDirector'].set_country_code()
            for mac in self.mac_list:
                logging.info("Remove AP %s out of the Access Points table" % mac)
                self.testbed.components['ZoneDirector'].remove_approval_ap(mac)
            #enable apprval police
            self.testbed.components['ZoneDirector'].set_ap_policy_approval()           
        # If ZD changes country code after APs join, make sure that APs are connecting to the Zone Director
        else:
            for mac in self.mac_list:
                if not self.testbed.components['ZoneDirector'].get_all_ap_info(mac)['status'].lower().startswith("connected"):
                    raise Exception("The AP %s is disconnected from the ZoneDirector" % mac)
            logging.info("The tested APs are joining the ZD now")

            time.sleep(2)
            logging.info("Change country code on the ZoneDirector")
            self.testbed.components['ZoneDirector'].set_country_code()
     

    def test(self):
        time.sleep(1)
        if self.is_ap_join_after_change:
            # APs has not joined the ZD, make sure that APs' entries can not immediately appear the AP-Summary table
            # after ZD change its country code
            for mac in self.mac_list:
                if self.testbed.components['ZoneDirector'].get_all_ap_info(mac):
                    return ["FAIL", "The AP %s is still under ZD control" % mac]
            logging.info("The tested APs are removed out of the AP-Summary table now")
        else:
            # APs are joining to the ZD, make sure that the tested APs is in Disconnected status
            # in the AP-Summary table after changing country code on the ZD
            for mac in self.mac_list:
                if not self.testbed.components['ZoneDirector'].get_all_ap_info(mac)['status'].lower().startswith("disconnected"):
                    return ["FAIL", "The AP %s is not in \"Disconnected\" status in the AP-Summary table" % mac]
            logging.info("The tested APs are in \"Disconnected\" status now")

        time.sleep(60)
        # Wait for the ZD makes provision for the non-country code locked AP
        approval_timeout = 240
        start_approval_time = time.time()
        while True:
            if (time.time() - start_approval_time) > approval_timeout:
                return ["FAIL", "The AP %s still disconnects from the ZoneDirector after %d seconds" % 
                        (self.mac_list[1], approval_timeout)]
            non_locked_ap = self.testbed.components['ZoneDirector'].get_all_ap_info(self.mac_list[1])
            if non_locked_ap:
                if non_locked_ap['status'].lower().startswith("connected"):
                    logging.info("The provision process for the AP %s is completed successfully" % self.mac_list[1])
                    break
            time.sleep(1)

        # Make sure that AP has obtained the same country code setting as the one configured on the ZoneDirector
        time.sleep(10)
        self.comp[1].verify_component()
        ap_country_code = self.comp[1].get_country_code()
        zd_country_code = self.testbed.components['ZoneDirector'].get_country_code()['value']

        if ap_country_code != zd_country_code:
            logging.info("The AP country code is %s" % ap_country_code)
            logging.info("The ZoneDirector country code is %s" % zd_country_code)
            return ["FAIL", "The AP %s and the ZoneDirector do not have the same country code setting" % self.mac_list[1]]
        logging.info("The AP %s and the ZD have the same country code setting" % self.mac_list[1])

        #Make sure that the country code locked AP can not join the ZD
        timeout = 60
        start_time = time.time()
        if self.is_ap_join_after_change:
            # If ZD changes country code before APs join, the country code locked AP's entry have never been appeared
            # in the AP-Summary table
            while True:
                locked_ap = self.testbed.components['ZoneDirector'].get_all_ap_info(self.mac_list[0])
                if locked_ap:
                    return ["FAIL", "The AP %s is still under ZD control" % self.mac_list[0]]
                if time.time() - start_time > timeout:
                    logging.info("The country code locked AP %s is completely disconnected from the ZoneDirector" % 
                                 self.mac_list[0])
                    break
                time.sleep(1)
        else:
            # If ZD changes country code after APs join, the non-country code locked AP is always in the "Disconnected" status
            while True:
                locked_ap = self.testbed.components['ZoneDirector'].get_all_ap_info(self.mac_list[0])
                if locked_ap['status'].lower().startswith("connected"):
                    return ["FAIL", "The AP %s is still in the \"Connected\" status" % self.mac_list[0]]
                if time.time() - start_time > timeout:
                    logging.info("The AP %s is in the \"Disconnected\" status now" % self.mac_list[0])
                    break
        return ["PASS", ""]

    def cleanup(self):
        time.sleep(10)
        logging.info("Return the old country code (%s) for the ZD" % self.old_ctrycode['label'])
        self.testbed.components['ZoneDirector'].set_country_code(self.old_ctrycode['label'])

        # Wait for APs rebooting after changing country code on the ZD
        clean_timeout = 240
        start_clean_time = time.time()
        while True:
            if time.time() - start_clean_time > clean_timeout:
                raise Exception("The APs do not connect to the ZoneDirector after %d seconds" % clean_timeout)
            aps_info = self.testbed.components['ZoneDirector'].get_all_ap_info()
            count = 0
            for ap_info in aps_info:
                if ap_info['status'].lower().startswith("connected"):
                    count = count + 1
            if count == len(aps_info):
                time.sleep(10)
                break
            time.sleep(1)

        self.testbed.components['ZoneDirector'].set_ap_policy_approval(self.old_status)

        time.sleep(10)
        logging.info("Return the old configuration for APs on the ZD")
        for ap_cfg in self.current_aps_cfg:
            self.testbed.components['ZoneDirector'].set_ap_cfg(ap_cfg)
            time.sleep(1)

        if len(self.comp) == 1:
            self.comp[0].verify_component()
            logging.info("Return the old country code status for the country code locked AP %s" % self.mac_list[0])
            if self.old_ctrycode_locked != self.comp[0].get_fixed_country_code():
                self.comp[0].set_fixed_country_code(False)
        elif len(self.comp) == 2:
            self.comp[0].verify_component()
            logging.info("Return the old country code status for the country code locked AP %s" % self.mac_list[0])
            if self.old_ctrycode_locked != self.comp[0].get_fixed_country_code():
                self.comp[0].set_fixed_country_code(False)

            self.comp[1].verify_component()
            logging.info("Return the old country code status for the non-country code locked AP %s" % self.mac_list[1])
            if self.old_ctrycode_unlocked != self.comp[1].get_fixed_country_code():
                self.comp[1].set_fixed_country_code()
        logging.info("-------- FINISHIED --------\n")


