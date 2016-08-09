# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedType description.
# This should also document the config parameters that this testbed understands.
"""
CPE_Stations Testbed is the testbed type mainly designed for CPE/Metro Flex model
to test CPE interfaces. It consists of 1 components:

1) One or more remote stations

This testbed understands the following config parameters:
'sta_ip_list': list of station IP Address in the testbed.

Example parameter: 
{'sta_ip_list':['192.168.1.12'], 
'cfg_file_name':'./RuckusAutoTest/common/CPE_Testbed_Info_Default.inf', 
'mf_ip_dict':{'mf2211':['192.168.10.188'],}}

Notes:
cfg_file_name is the config file for CPE upgrade settings.
mf_ip_dict include mode and related ip address.

"""
import logging

from RuckusAutoTest.models import TestbedBase
from RuckusAutoTest.components import create_station_by_ip_addr


# Note that the name of the testbed class must match the name of this file for ease of runtime-reference

class CPE_Stations(TestbedBase):
    def __init__(self, testbedinfo, config):
        TestbedBase.__init__(self, testbedinfo,config)        
        self.testbed_info = testbedinfo
        
        # Initiate station component
        
        self.components['Station']=[]
        ip_list = self.config['sta_ip_list']
        for ip_addr in ip_list:
            station = create_station_by_ip_addr(ip_addr = ip_addr)
            self.components['Station'].append(station)
            
            #self.components['Station'].append(RemoteStationWinPC.RemoteStationWinPC(sta_dict))
                
    def verifyTestbed(self):
        """ Loop through the testbed components and rely on components to verify themselves"""
        # Exceptions should be handled in components level
        # To be added: testbed devices not implemented as component may need to be verified, e.g
        # DHCP server, etc.
        logging.info ("Testbed %s Verifying component" % (self.testbed_info.name))
        #self.AP.verify_component()
        for index, item in enumerate(self.components['Station']):
            item.verify_component()           