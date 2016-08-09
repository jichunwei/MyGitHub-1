# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedType description.
# This should also document the config parameters that this testbed understands.
"""
AP_ATT Testbed is the testbed type mainly designed for standalone AP and Adatper
to test ATT. It consists of 3 components:

1) Standalone AP DUT
2) 2 remote window station
3  2 ruckus adapter

This testbed understands the following config parameters:

Example parameter:

Notice: rootpath is file system path where TFTP/FTP server stores file
- Windows: 'rootpath': 'c:\\ftp' or 'rootpath': 'c:\\tftpboot'
- Linux: 'rootpath':'/ftp' or 'rootpath':'/tftpboot'
"""
import time
import logging
#import sys
import os
import re
from RuckusAutoTest.models     import TestbedBase
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components import RemoteStationWinPC


# Note that the name of the testbed class must match the name of this file for ease of runtime-reference

class AP_ATT(TestbedBase):
    def __init__(self, testbedinfo, config):
        TestbedBase.__init__(self, testbedinfo, config)
        self.testbed_info = testbedinfo

        # Initialize station components
        self.components['Station'] = []
        ip_list = self.config['win_sta_list']
        for i in range(len(ip_list)):
            sta_dict = {}
            sta_dict['sta_ip_addr'] = ip_list[i]
            self.components['Station'].append(RemoteStationWinPC.RemoteStationWinPC(sta_dict))

        del self.config['win_sta_list']

        # Initialize dut component
        self.components['AP'] = []
        self.dict_aps = config['ap_sym_dict']
        for ap in self.dict_aps.keys():
            ap_config = self.dict_aps[ap]

            # change back later
            self.dict_aps[ap]['log_file'] = file(os.path.join("logs", "log_%s_%s_cli_%s.txt" %
                                                        (testbedinfo.name, ap, time.strftime("%Y%m%d%H%M"))), 'w')

            self.components['AP'].append(RuckusAP(ap_config))



    def verifyTestbed(self):
        """ Loop through the testbed components and rely on components to verify themselves"""
        # Exceptions should be handled in components level
        # To be added: testbed devices not implemented as component may need to be verified, e.g
        # DHCP server, etc.
        logging.info ("Testbed %s Verifying component" % (self.testbed_info.name))

    def getAPIpAddrBySymName(self, ap_sym_name):
        if re.match(r'^[0-9.]+$', ap_sym_name):
            return ap_sym_name
        if self.ap_dict and self.ap_dict.has_key(ap_sym_name):
            return self.ap_dict[ap_sym_name]['ip_addr']
        raise "AP symbolic name '%s' does not defined at testbed's attr 'ap_sym_dict'" % ap_sym_name

    def getAdIpAddrBySymName(self, ad_sym_name):
        if re.match(r'^[0-9.]+$', ad_sym_name):
            return ad_sym_name
        if self.ad_dict and self.ad_dict.has_key(ad_sym_name):
            return self.ad_dict[ad_sym_name]['ip_addr']
        raise "AP symbolic name '%s' does not defined at testbed's attr 'ad_sym_name'" % ad_sym_name

