# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module doc string is accurate since it will be used in report generation.

"""Description

    Prerequisite (Assumptions about the state of the testbed/DUT):

    Required components:
    Test parameters:
    Result type: PASS/FAIL
    Results: PASS
             FAIL otherwise

    Messages:
        - If PASS,
        - If FAIL, prints out the reason for failure

    Test procedure:
    1. Config:
        -
    2. Test:
        -
    3. Cleanup:
        -

    How is it tested: (to be completed by test code developer)

"""
import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Remove_All_L2_ACLs(Test):
    required_components = ["ZoneDirector"]
    parameter_description = {}
    
    def config(self, conf):
        self._initTestParameters(conf)
    
    def test(self):
        # Try to remove all wlans on ZD, if exception is raised, catch it and try to remove again
        # If timeout is expired and wlans can not be removed, raise exception
        if self.remove_wlan:
            self._remove_all_wlan()
            
        logging.info("Remove all ACL rules on the Zone Director")
        self.zd.remove_all_acl_rules()

        if self.target_station:
            logging.info("Remove all WLAN profiles on the remote station")
            self.target_station.remove_all_wlan()

            logging.info("Make sure the target station disconnects from the wireless networks")
            start_time = time.time()
            while True:
                if self.target_station.get_current_status() == "disconnected":
                    break
                time.sleep(1)
                if time.time() - start_time > self.check_status_timeout:
                    raise Exception("The station did not disconnect from wireless network within %d seconds" % 
                                    self.check_status_timeout)
        if self.errmsg:
            return ("FAIL", self.errmsg)
        
        return ("PASS", 'all of ACLs are removed.')
    
    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'remove_wlan':True}
        self.conf.update(conf)
        self.remove_wlan = self.conf['remove_wlan']
        self.zd = self.testbed.components['ZoneDirector']
                
        self.check_status_timeout = 120
        self.target_station = None
                            
        self.errmsg = ''
        self.passmsg = ''
            
    def _retrive_carrier_bag(self):
        pass

    def _update_carrier_bag(self):
        pass        
    
    def _remove_all_wlan(self):
        """
        Remove all the WLANs.
        """
        try:
            lib.zd.wlan.delete_all_wlans(self.zd)
            self.passmsg = 'All WLANs are deleted successfully'
            logging.debug(self.passmsg)
        except Exception, e:
            self.errmsg = '[WLANs deleting failed] %s' % e.message
            logging.debug(self.errmsg)        
    
    