# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedType description.
# This should also document the config parameters that this testbed understands.
"""
AP_Single_Station Testbed is the testbed type mainly designed for standalone AP
to test AP interfaces. It consists of 3 components:

1) Standalone AP DUT
2) Test Engine with wireless adapter and 2 ethernet NICs

This testbed understands the following config parameters:

'AP_Type'    : A dictionary contains AP information(ip_addr,username,password and information of FTP server component)
'sta_ip_addr'   : IP address of test engine

Example parameter:
{'ZF7942':{'ip_addr':'192.168.0.100','username':'super','password':'sp-admin',
'ftpsvr':{'ip_addr':'192.168.0.20', 'username':'anonymous','password':'anonymous','rootpath':'c:\\\\ftp'}},
'sta_ip_addr':'192.168.1.21'}

Notice:
1. rootpath is file system path where TFTP/FTP server stores file
- Windows: 'rootpath': 'c:\\ftp' or 'rootpath': 'c:\\tftpboot'
2. The current version this testbed only support Test Engine that run Windows
"""
import sys
import time
import logging

from RuckusAutoTest.models import TestbedBase
from RuckusAutoTest.components import *


# Note that the name of the testbed class must match the name of this file for ease of runtime-reference

class AP_Single_Station(TestbedBase):
    def __init__(self, testbedinfo, config):
        TestbedBase.__init__(self, testbedinfo,config)
        self.testbed_info = testbedinfo

        # Initiate station component
        self.components['Station']=[]
        sta_dict = {}
        sta_dict['sta_ip_addr'] = self.config['sta_ip_addr']
        self.components['Station'].append(StationWinPC.StationWinPC(sta_dict))
        del config['sta_ip_addr'] # delete keys to make config only has dut info

        # Initiate dut component
        self.components['AP'] = []        
        for ap_type in config.keys():
            config[ap_type]['log_file'] = file("log_%s_%s_cli_%s.txt" %(testbedinfo.name,ap_type,time.strftime("%Y%m%d%H%M")),'w')
            
            # get AP type by name 
            logging.debug("AP Type: %s" % ap_type)            
            apclass = sys.modules['RuckusAutoTest.components'].__dict__[ap_type].__dict__[ap_type]                        
            self.AP = apclass(config[ap_type])            
            self.dut = self.AP
            self.components['AP'].append(self.AP)
            self.components[ap_type] = self.AP 
            
    def verifyTestbed(self):
        """ Loop through the testbed components and rely on components to verify themselves"""
        # Exceptions should be handled in components level
        # To be added: testbed devices not implemented as component may need to be verified, e.g
        # DHCP server, etc.
        logging.info ("Testbed %s Verifying component" % (self.testbed_info.name))
        self.AP.verify_component()
        for index, item in enumerate(self.components['Station']):
            item.verify_component()
