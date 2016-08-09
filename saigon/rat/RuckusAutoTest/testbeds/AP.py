# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedType description.
# This should also document the config parameters that this testbed understands.
"""
AP Testbed is the simplest testbed type mainly designed for development Engineers
to test AP interfaces. It consists of only one component:

1) Standalone AP as DUT, based on generic RuckusAP implementation

This testbed understands the following config parameters:
'ap'    : A dictionary contains AP information(ip_addr,username,password and information of FTP server component)

Example parameter:
{'ap':{'ip_addr':'192.168.0.1','username':'super','password':'sp-admin',
'ftpsvr':{'ip_addr':'192.168.0.20', 'usrname':'anonymous','password':'blank','rootpath':'c:\\ftp'}}}

Notice: rootpath is file system path where TFTP/FTP server stores file
- Windows: 'rootpath': 'c:\\ftp' or 'rootpath': 'c:\\tftpboot'
- Linux: 'rootpath':'/ftp' or 'rootpath':'/tftpboot'
"""

import time

from RuckusAutoTest.models import *
from RuckusAutoTest.components.RuckusAP import RuckusAP


# Note that the name of the testbed class must match the name of this file for ease of runtime-reference

class AP(TestbedBase):
    def __init__(self, testbedinfo, config):
        TestbedBase.__init__(self, testbedinfo,config)
        config['ap']['log_file'] = file("log_%s_ap_cli_%s.txt" %(testbedinfo.name,time.strftime("%Y%m%d%H%M")),'w')
        self.testbedinfo = testbedinfo
        self.AP = RuckusAP(config['ap'])
        self.dut = self.AP
        self.components['RuckusAP'] = self.AP
        self.VerifyTestbed()

    def verifyTestbed(self):
        """ Loop through the testbed components and rely on components to verify themselves"""
        # Exceptions should be handled in components level
        # To be added: testbed devices not implemented as component may need to be verified, e.g
        # DHCP server, etc.
        logging.info ("Testbed %s Verifying component" % (self.testbed_info.name))
        self.dut.verify_component()

