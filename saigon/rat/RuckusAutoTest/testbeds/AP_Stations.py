# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedType description.
# This should also document the config parameters that this testbed understands.
"""
AP_Stations Testbed is the testbed type mainly designed for standalone AP
to test AP interfaces. It consists of 3 components:

1) Standalone AP DUT
2) One or more remote stations

This testbed understands the following config parameters:
'sta_ip_list': list of station IP Address in the testbed. 
'AP_Type': A dictionary contains AP information(ip_addr,username,password and information of FTP server component)
'ap_conf': 

Example parameter: 
{'sta_ip_list': ['192.168.1.31'], 
 'ZF2925': {'ip_addr': '192.168.0.250'}, 
 'ap_conf': {'username': 'super', 'password': 'sp-admin', 
 'ftpsvr': {'username': 'anonymous', 'protocol': 'FTP', 'password': 'anonymous', 
            'ip_addr': '192.168.0.21', 'rootpath': 'c:\\\\tftpboot'}}}

Notice: rootpath is file system path where TFTP/FTP server stores file 
- Windows: 'rootpath': 'c:\\ftp' or 'rootpath': 'c:\\tftpboot' 
- Linux: 'rootpath':'/ftp' or 'rootpath':'/tftpboot' 
"""
import time 
import logging
import sys

from RuckusAutoTest.models import TestbedBase
from RuckusAutoTest.components import *


# Note that the name of the testbed class must match the name of this file for ease of runtime-reference

class AP_Stations(TestbedBase):
    def __init__(self, testbedinfo, config):
        TestbedBase.__init__(self, testbedinfo,config)        
        self.testbed_info = testbedinfo

        # Initiate station component
        self.components['Station']=[]
        ip_list = self.config['sta_ip_list']
        for i in range(len(ip_list)):
            sta_dict = dict()            
            sta_dict['sta_ip_addr'] = ip_list[i]
            self.components['Station'].append(RemoteStationWinPC.RemoteStationWinPC(sta_dict))
        # get general ap configuration from testbed
        ap_config = self.config['ap_conf'].copy()      
        
        del self.config['sta_ip_list']
        del self.config['ap_conf']
        # Initiate dut component
        self.components['AP'] = []        
        for ap_type in config.keys():            
            config[ap_type]['log_file'] = file("log_%s_%s_cli_%s.txt" %
                                              (testbedinfo.name,ap_type,time.strftime("%Y%m%d%H%M")),'w')
            config[ap_type].update(ap_config)            
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
