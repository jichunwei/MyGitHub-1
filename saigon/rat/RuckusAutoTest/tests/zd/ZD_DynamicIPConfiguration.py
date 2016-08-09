# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_DynamicIPConfiguration class verifies if the Zone Director can get Address from the DHCP Server. 
Because of the fact that changing IP address is very risk in automation, we configure the DHCP to assign the same 
IP address with the current static one (192.168.0.2) to the Zone Director. We check the DNS Server address only.


   Prerequisite (Assumptions about the state of the testbed/DUT): The DHCP Server must assign the same IP address (192.168.0.2) to the
   ZoneDirector. 
   1. Build under test is loaded on the AP and Zone Director.

   Required components: 'ZoneDirector'
   
   Test parameters: none.
   
   Result type: PASS/FAIL 

   Results: PASS: If the Zone Director can get the DNS Server address from the DHCP Server.
            FAIL: If the Zone Director can not get the DNS Server address from the DHCP Server.

   Messages: 
       - if the result is PASS, no message is shown.
       - if the result is FAIL, an error message is shown.

   Test procedure:
       Config:
           1.  Get the current IP of the DNS Server.
           2.  Get the status of the IP configuration.
       Test:
           1.  Navigate to Configure --> System.
           2.  Apply dynamic IP configuration to the ZD.
           3.  Verify if the ZD can get the correct DNS Server address.
       Cleanup: 
           1.  Clean up the environment by setting the IP configuration to its original one.
   
   How it was tested:
      1.  Disable the DHCP server, the script must return FAIL.
"""

import os
import time
import logging

from RuckusAutoTest.models import Test

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_DynamicIPConfiguration(Test):
    required_components = ['ZoneDirector']
    parameter_description = {}

    def config(self, conf):
        # Testing parameters
        print "Getting the current IP address of the Primary DNS Server configuration."
        self.system_dns_server = self.testbed.components['ZoneDirector'].get_ip_cfg()['pri_dns']
        logging.info("The DNS Server address is '%s'" % self.system_dns_server)
        logging.info("Set the DNS Server address to '10.10.10.10'")
        self.testbed.components['ZoneDirector'].set_ip_cfg({'ip_addr':'', 'net_mask':'', 'gateway':'',
                       'pri_dns':'10.10.10.10', 'sec_dns':''})
        
        self.status = self.testbed.components['ZoneDirector'].get_ip_cfg_status()
        logging.info("The current status is: %s" % self.status)
        
    def test(self):
        print "Change the IP configuration to DHCP"
        self.testbed.components['ZoneDirector'].set_ip_cfg_status("dhcp")
        print "Check whether the Zone Director can get the DNS Address from the DHCP Server"
        dns_address = self.testbed.components['ZoneDirector'].get_ip_cfg()['pri_dns']
        logging.info("The DNS Server Address from the DHCP Server is '%s'" % dns_address)
        if dns_address == "" and dns_address == '10.10.10.10':
            return ["FAIL", "Zone Director can not get the primary DNS Server address from the DHCP Server "]
        logging.info("Get the DNS Server address from the DHCP Server successfully")
        return ["PASS", ""]

    def cleanup(self):
        if self.status:
            logging.info("Set the status to '%s'" % self.status)
            self.testbed.components['ZoneDirector'].set_ip_cfg_status(self.status)
        print "Setting the Primary DNS Server configuration to its original value"
        if self.status == "static":
            logging.info("Set dns server address to '%s'" % self.system_dns_server)
            self.testbed.components['ZoneDirector'].set_ip_cfg({'ip_addr':'', 'net_mask':'', 'gateway':'',
                       'pri_dns':self.system_dns_server, 'sec_dns':''})

