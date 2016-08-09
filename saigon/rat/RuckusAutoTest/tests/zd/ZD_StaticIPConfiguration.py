# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_StaticIPConfiguration class tests the IP configuration of the Zone Director. 

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director.

   Required components: 'ZoneDirector'
   
   Test parameters: no. But we can add more values to the dictionary 'valid_ip_dict' and 'invalid_ip_dict'. 
                    These values base on the below applied list. Please note that, because of the Automation's limitation, 
                    the valid IP must be in the subnet 192.168.0.x/24.
   
   Result type: PASS/FAIL 

   Results: PASS: Accepts all valid values, denies all the invalid values with correct alert messages.
            FAIL: Accepts at least one invalid value or denies at least one valid value.  

   Messages: 
       - if the result is PASS, no message is shown. 
       - if the result is FAIL, an error message will be shown.

   Applied value list:
       1.   A valid IP ('192.168.0.123',...).
       2.   Two IPs separated by space(s) ('192.168.0.23 192.168.0.45',...).
       3.   A string with non-numeric character(s) ('192.168.1.a45',...).
       4.   A subnet address (we skip this one because of the automation's limitation).
       5.   An out-of-range IP. (192.1000.12.255).
       6.   A broadcast IP address (we skip this one because of the automation's limitation).
       7.   An IP followed by space(s) ('192.168.0.25    ',...).
       8.   An IP preceeded by space(s) ('    192.168.0.56',...).
           
   Testing procedure:
       Config:
           1.   Navigate to Configure --> System.
           2.   Get the current IP configuration.
       Test       
           1.   Apply each item in the above applied value list to the IP address/Netmask/Default Gateway/ DNS Server/
                2DNS Server then apply the changes.
           2.   Verify if the ZD web UI reacts properly. A message should be shown if an invalid IP is applied.
       Cleanup:
           1.   Clean up the environment by setting the Zone Director to its original configuration.
       
   How it was tested:
       1. Enter a valid name to this list of invalid names.
       2. Enter an invalid name to the list of valid names.
"""

import os
import time
import logging

from RuckusAutoTest.models import Test

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_StaticIPConfiguration(Test):
    required_components = ['ZoneDirector']
    parameter_description = {}

    def config(self, conf):
        # Testing parameters
        self.ip_cfg_dict = None
        logging.info("Getting the current IP configuration.")
        self.ip_cfg_dict = self.testbed.components['ZoneDirector'].get_ip_cfg()
        logging.info("The current IP configuration is: %s" % self.ip_cfg_dict)
                
    def test(self):
        # Because the limitation of automation, ip address must be in the same subnet with the original one.
        # JLIN@20081112 modify sys_net_mask 255.255.255.128 to 255.255.255.0 for ZD70
        valid_ip_dict = {'sys_ip_address':["192.168.0.123"], \
                         'sys_net_mask':["255.0.0.0", \
                                        "255.255.0.0", \
                                        "255.255.255.0"], \
                         'sys_default_gateway':["192.168.0.20"], \
                         'sys_dns_server':["192.168.10.12"], \
                         'sys_dns2_server':["192.168.20.15"]}        
        # we skip the items 4 and 6 in the applied list due to the limitation of automation. 
        # You can add more invalid ip addresses to the list
        #@author: Jane.Guo @since: 2013-09 behavior change         
        invalid_ip_dict = {'sys_ip_address':["192.168.0.123 192.168.0.45", \
                                             "192.168.a12.5", \
                                             "192.168.1000.12", \
                                             "   192.16 8.0.123", \
                                             "192.168..0.123"], \
                           'sys_net_mask':["255.0.12.0", \
                                          "255.255.255.121", \
                                          "192.168.0.123 192.168.0.45", \
                                          "192.168.a12.5", \
                                          "192.168.1000.12", \
                                          "192.168 .0.123   ", \
                                          "192.168...0.123"], \
                           'sys_default_gateway':["192.168.0.123 192.168.0.45", \
                                                  "192.168.a12.5", \
                                                  "192.168.1000.12", \
                                                  "192.168. 0.123", \
                                                  "192.168..0.123"], \
                           'sys_dns_server':["192.168.0.123 192.168.0.45", \
                                             "192.168.a12.5", \
                                             "192.168.1000.12", \
                                             "192.16 8.0.123", \
                                             "192.168..0.123"], \
                           'sys_dns2_server':["192.168.0.123 192.168.0.45", \
                                              "192.168.a12.5", \
                                              "192.168.1000.12", \
                                              "192.168.0. 123", \
                                              "192.168..0.123"]}
        
        # Processing the list of valid ip addresses.
        for ip_type, ip_list in valid_ip_dict.items():
            for an_ip in ip_list:
                try:
                    if ip_type == 'sys_ip_address':
                        ip_cfg = {'ip_addr':an_ip, 'net_mask':'', 'gateway':'',
                                  'pri_dns':'', 'sec_dns':''}   
                        self.testbed.components['ZoneDirector'].set_ip_cfg(ip_cfg)
                    elif ip_type == 'sys_net_mask':
                        ip_cfg = {'ip_addr':'', 'net_mask':an_ip, 'gateway':'',
                                  'pri_dns':'', 'sec_dns':''}   
                        self.testbed.components['ZoneDirector'].set_ip_cfg(ip_cfg)
                    elif ip_type == 'sys_default_gateway':
                        ip_cfg = {'ip_addr':'', 'net_mask':'', 'gateway':an_ip,
                                  'pri_dns':'', 'sec_dns':''}   
                        self.testbed.components['ZoneDirector'].set_ip_cfg(ip_cfg)
                    elif ip_type == 'sys_dns_server':
                        ip_cfg = {'ip_addr':'', 'net_mask':'', 'gateway':'',
                                  'pri_dns':an_ip, 'sec_dns':''}   
                        self.testbed.components['ZoneDirector'].set_ip_cfg(ip_cfg)
                    else:
                        ip_cfg = {'ip_addr':'', 'net_mask':'', 'gateway':'',
                                  'pri_dns':'', 'sec_dns':an_ip}   
                        self.testbed.components['ZoneDirector'].set_ip_cfg(ip_cfg)                        
                        
                except Exception, e:
                    return ["FAIL", "Zone Director does not accept a valid ip address '%s' as %s. \
                    The message is '%s'" % (an_ip, ip_type, e.message)]
                
        # Processing the list of invalid ip addresses.
        for ip_type, ip_list in invalid_ip_dict.items():
            for an_ip in ip_list:
                try:
                    if ip_type == 'sys_ip_address':
                        ip_cfg = {'ip_addr':an_ip, 'net_mask':'', 'gateway':'',
                                  'pri_dns':'', 'sec_dns':''}   
                        self.testbed.components['ZoneDirector'].set_ip_cfg(ip_cfg)
                    elif ip_type == 'sys_net_mask':
                        ip_cfg = {'ip_addr':'', 'net_mask':an_ip, 'gateway':'',
                                  'pri_dns':'', 'sec_dns':''}   
                        self.testbed.components['ZoneDirector'].set_ip_cfg(ip_cfg)
                    elif ip_type == 'sys_default_gateway':
                        ip_cfg = {'ip_addr':'', 'net_mask':'', 'gateway':an_ip,
                                  'pri_dns':'', 'sec_dns':''}   
                        self.testbed.components['ZoneDirector'].set_ip_cfg(ip_cfg)
                    elif ip_type == 'sys_dns_server':
                        ip_cfg = {'ip_addr':'', 'net_mask':'', 'gateway':'',
                                  'pri_dns':an_ip, 'sec_dns':''}   
                        self.testbed.components['ZoneDirector'].set_ip_cfg(ip_cfg)
                    else:
                        ip_cfg = {'ip_addr':'', 'net_mask':'', 'gateway':'',
                                  'pri_dns':'', 'sec_dns':an_ip}   
                        self.testbed.components['ZoneDirector'].set_ip_cfg(ip_cfg)   
                        
                    return ["FAIL", "Zone Director accepts an invalid value '%s' as '%s'" % (an_ip, ip_type)]
                except:
                    pass
        return ["PASS", ""]

    def cleanup(self):
        print "Clean up: Set the System IP configuration to its original value"
        if self.ip_cfg_dict:
            self.testbed.components['ZoneDirector'].set_ip_cfg(self.ip_cfg_dict)
        

