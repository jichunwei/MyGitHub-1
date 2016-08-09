# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedType description.
# This should also document the config parameters that this testbed understands.
"""
AP_IPTV Testbed is the testbed type mainly designed for standalone AP and Adatper
to test IPTV. It consists of 3 components:

1) Standalone AP DUT
2) 2 remote linux station
3  2 ruckus adapter

This testbed understands the following config parameters:

Example parameter:

Notice: rootpath is file system path where TFTP/FTP server stores file
- Windows: 'rootpath': 'c:\\ftp' or 'rootpath': 'c:\\tftpboot'
- Linux: 'rootpath':'/ftp' or 'rootpath':'/tftpboot'
"""
import time
import logging
import sys
import os
import re
from RuckusAutoTest.models     import TestbedBase
from RuckusAutoTest.components import StationLinuxPC
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components import StationWinPC
from RuckusAutoTest.components import RuckusAPSerial


# Note that the name of the testbed class must match the name of this file for ease of runtime-reference

class AP_IPTV(TestbedBase):
    def __init__(self, testbedinfo, config):
        TestbedBase.__init__(self, testbedinfo, config)
        self.testbed_info = testbedinfo

        # Initialize station components
        self.components['Station'] = []
        ip_list = self.config['linux_sta_list']
        for i in range(len(ip_list)):
            sta_dict = {}
            sta_dict['sta_ip_addr'] = ip_list[i]
            self.components['Station'].append(StationLinuxPC.StationLinuxPC(sta_dict))

        ip_list = self.config['win_sta_list']
        for i in range(len(ip_list)):
            sta_dict = {}
            sta_dict['sta_ip_addr'] = ip_list[i]
            self.components['Station'].append(StationWinPC.StationWinPC(sta_dict))

        ap_config = self.config['ap_conf'].copy()
        self.sta_wifi_subnet = self.config['sta_wifi_subnet'].copy()
        self.sta_wireless_interface_info = self.config['sta_wireless_interface_info'].copy()
        self.sta_pppoe_subnet = self.config['sta_pppoe_subnet'].copy()
        self.ftpserv = self.config['ftpserv'].copy()
        self.pwr_mgmt = self.config['pwr_mgmt'].copy()

        del self.config['linux_sta_list']
        del self.config['win_sta_list']
        del self.config['ap_conf']
        del self.config['sta_wifi_subnet']
        del self.config['sta_wireless_interface_info']
        del self.config['sta_pppoe_subnet']
        del self.config['ftpserv']
        del self.config['pwr_mgmt']

        # Initialize dut component
        self.components['AP'] = []
        self.ap_dict = config['ap_sym_dict']
        # TODO: In test/ap/libITV_TestConfig.getTestbedActiveAP uses var with
        # name dict_aps to iter active APs in testbed but the AP_IPTV class don't
        # define this var so it causes error. The new getTestbedActiveAP method
        # comes from ATT
        # Temporarily, work around by adding dict_aps =  ap_dict
        self.dict_aps = self.ap_dict
        for key in self.ap_dict.keys():
            if not self.ap_dict[key].has_key('username'):
                self.ap_dict[key].update(ap_config)
            #self.ap_dict[key]['log_file'] = file(os.path.join("logs", "log_%s_%s_cli_%s.txt" %
            #                                           (testbedinfo.name, key, time.strftime("%Y%m%d%H%M"))), 'w')
            self.ap_dict[key]['log_file'] = file('test.txt', 'w')
            if not self.ap_dict[key].has_key('use_serial'):
                self.components['AP'].append(RuckusAP(self.ap_dict[key]))
            else:
                self.components['AP'].append(RuckusAPSerial.RuckusAPSerial(self.ap_dict[key]))

        self.ad_list = []
        self.ad_dict = config['ad_sym_dict']
        for key in self.ad_dict.keys():
            if not self.ad_dict[key].has_key('username'):
                self.ad_dict[key].update(ap_config)
            self.ad_list.append(self.ad_dict[key])

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

    def __del__(self):
        logging.info('Release all station connections')
        del self.components['Station']
