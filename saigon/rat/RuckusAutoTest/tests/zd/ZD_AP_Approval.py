# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_AP_Approval Test class tests the ability of APs to join the ZoneDirector by manual or automatic approval.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector', 'RuckusAP'
   Test parameters: 'auto_approval': 'This is the bool value used to decide if the verified APs is automatically approved
                                      to join the ZD or not.
                                     If auto_approval is True, the APs will automatically discover and join the ZD.
                                     If auto_approval is False, the APs will be manually approved to join the ZD'

   Result type: PASS/FAIL
   Results: PASS: The APs can join the ZD (manually or automatically), be made provision from ZD successfully,
                   and be in RUN state at the CLI mode.
            FAIL:  If one of the above criteria is not met.

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - Navigate to Configure/Access Points page, remove all APs in the Access Points table
       - Set AP approval policy based on the 'auto_approval' value
   2. Test:
       -  Navigate to the Monitor/Access Points to verify that the AP-Summary is empty after removing
          all APs out of the ZoneDirector
       -  If auto_approval is True, APs should discover and join the ZoneDirector successfully.
          If auto_approval is False, APs should be manual approved by clicking "allow" span at
          Monitor/AccessPoints page.
       -  Verify that Zone Director makes provision for APs successfully by checking the status of these APs
          in the AP-Summary table which should be "Connected".
       -  At AP CLI mode, using command "get director-info" to make sure that APs are in the RUN state
   3. Cleanup:
       - Return the old AP approval policy for the ZoneDirector

    How it was tested:
        1. In the manual AP approval case, when APs are rebooting, login to the ZD's GUI, check the approval checkbox at
           Configure/AccessPoints page to make ZD automatically approve for APs join.
           The test script will return FAIL result because there's no status "Pending Approval" of any APs
           appeared in the AP-Summary table.

        2. In the automatic AP approval case, when APs are rebooting, login to the ZD's GUI, uncheck the approval checkbox at
           Configure/AccessPoints page to make ZD manually approve for APs join.
           The test script will return FAIL result because APs can not join the ZD.
"""

import time
import logging

from RuckusAutoTest.models import Test


class ZD_AP_Approval(Test):
    required_components = ['ZoneDirector', 'RuckusAP']
    parameter_description = {'auto_approval' :'This is the bool value used to decide if the tested \
                              AP is automatically approved to join the ZoneDirector or not'}

    def config(self, conf):
        self.auto_approval = conf['auto_approval']
        self.old_status = self.testbed.components['ZoneDirector'].get_ap_policy_approval()
        self.current_aps_cfg = []

        # Make sure that all APs in the testbed are connecting to the Zone Director
        start_time = time.time()
        timeout = 150
        while True:
            connected = 0
            self.aps_in_testbed = self.testbed.components['ZoneDirector'].get_all_ap_info()
            for ap in self.aps_in_testbed:
                if ap['status'].lower().startswith("connected"):
                    connected += 1
            if connected == len(self.testbed.components['AP']):
                break
            if time.time() - start_time > timeout:
                raise Exception("There are (is) %d AP(s) disconnected from the ZD" % 
                                (len(self.testbed.components['AP']) - connected))

        logging.info("Get the current configuration of APs on the ZD")
        for ap in self.aps_in_testbed:
            ap_cfg = self.testbed.components['ZoneDirector'].get_ap_cfg(ap['mac'])
            self.current_aps_cfg.append(ap_cfg)
            time.sleep(1)

        logging.info("Remove all APs out of the Access Points table")
        self.testbed.components['ZoneDirector'].remove_approval_ap()
        self.testbed.components['ZoneDirector'].set_ap_policy_approval(self.auto_approval)

        #Make sure that there are no APs existed in the AP-Summary table
        aps_info = self.testbed.components['ZoneDirector'].get_all_ap_info()
        if aps_info:
            raise Exception("The AP-Summary table is not empty after removing all APs")
        logging.info("The AP-Summary table is empty now")

    def test(self):
        if not self.auto_approval:
            logging.info("Manually approving for APs to join the ZoneDirector")
            timeout = 150
            start_time = time.time()
            while True:
                aps_info = self.testbed.components['ZoneDirector'].get_all_ap_info()
                if len(aps_info) == len(self.aps_in_testbed):
                    for ap in aps_info:
                        if ap['status'].lower().startswith('approval'):
                            logging.info("The AP with mac address %s in the \"Approval Pending\" status now" % ap['mac'])
                            logging.info("Approve for this AP to join the ZD")
                            self.testbed.components['ZoneDirector'].allow_ap_joining(ap['mac'])
                            time.sleep(1)
                        else:
                            logging.debug("AP info: %s" % str(ap))
                            return ["FAIL", "The AP with mac address %s is in %s status instead of the\
                                    \"Approval Pending\" status" % (ap['mac'], ap['status'])]
                    break

                if time.time() - start_time > timeout:
                    aps_temp = []
                    if aps_info:
                        for ap in self.aps_in_testbed:
                            if not ap in aps_info:
                                aps_temp.append(ap)
                        logging.debug("List of the APs appearing APs the AP-Summary table: %s" % str(aps_info))
                        logging.debug("List of the APs disappearing from the AP-Summary table: %s" % str(aps_temp))
                        return ["FAIL", "There are %d APs still disappearing from in the AP-Summary table after %d seconds" % 
                                (len(aps_temp), timeout)]

                    return ["FAIL", "APs do not appear in the AP-Summary table after %d seconds" % timeout]

        logging.info("Wait for the ZoneDirector makes provision for the APs")
        approval_timeout = 240
        start_approval_time = time.time()
        while True:
            provision = 0
            aps_info = self.testbed.components['ZoneDirector'].get_all_ap_info()
            if len(aps_info) == len(self.aps_in_testbed):
                for ap_info in aps_info:
                    if ap_info['status'].lower().startswith("connected"):
                        provision = provision + 1
                if provision == len(aps_info):
                    logging.info("The provision process for APs is completed successfully")
                    break
            if (time.time() - start_approval_time) > approval_timeout:
                aps_temp = []
                if len(aps_info) != len(self.aps_in_testbed):
                    for ap in self.aps_in_testbed:
                        if not ap in aps_info:
                            aps_temp.append(ap)
                    logging.debug("List of APs disappearing from the AP-Summary table: %s" % str(aps_temp))
                    return ["FAIL", "There are %d APs still disappearing from the AP-Summary table after %d seconds" % 
                            (len(aps_temp), approval_timeout)]

                for ap in aps_info:
                    if not ap['status'].lower().startswith("connected"):
                        aps_temp.append(ap)
                logging.debug("The disconnected APs list: %s" % str(aps_temp))
                return ["FAIL", "There are %d APs not in the \"Connected\" status after %d seconds" % 
                        (len(aps_temp), approval_timeout)]

        # Make sure that the APs are in RUN state at CLI mode
        for comp in self.testbed.components['AP']:
            comp.verify_component()
            if comp.get_director_info() != "RUN":
                return ["FAIL", "The AP with mac %s is not in the RUN state" % comp.get_base_mac()]
            logging.info("The AP with mac %s is in the RUN state now" % comp.get_base_mac())

        return ["PASS", ""]

    def cleanup(self):
        logging.info("Return the old approval policy for ZoneDirector")
        self.testbed.components['ZoneDirector'].set_ap_policy_approval(self.old_status['approval'])

        logging.info("Return the old configuration for APs")
        time.sleep(10)
        for ap_cfg in self.current_aps_cfg:
            self.testbed.components['ZoneDirector'].set_ap_cfg(ap_cfg)
            time.sleep(1)

        logging.info("--------- FINISHED --------\n")

