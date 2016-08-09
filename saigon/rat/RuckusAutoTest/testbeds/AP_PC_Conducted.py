# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedType description.
# This should also document the config parameters that this testbed understands.
"""
A VPT-like setup consisting of:

1) Standalone AP DUT
2) PC station
3) Attentuation device such as a RUCA

Communication between the PC station and the AP is via conducted channel and subject
to variable attentuation.

In the minimalist implementation the testbed controller PC and the PC station are the same device.

This testbed understands the following config parameters:

'APIP' : The AP DUT's IP address for communicating with the testbed.
"""
import time
import logging

from RuckusAutoTest.models import TestbedBase
from RuckusAutoTest.components.StationWinPC import StationWinPC
from RuckusAutoTest.components.RuckusAP import RuckusAP

# Note that the name of the testbed class must match the name of this file for ease of runtime-reference

class AP_PC_Conducted(TestbedBase):
    def __init__(self, testbedinfo, config):
        TestbedBase.__init__(self, testbedinfo,config)
        self.testbed_info = testbedinfo

        self.Station = StationWinPC()
        self.components['Station'] = self.Station

        config['ap']['log_file'] = file("log_%s_ap_cli_%s.txt" %(testbedinfo.name, time.strftime("%Y%m%d%H%M")),'w')
        self.AP = RuckusAP(config['ap'])
        self.dut = self.AP
        self.components['RuckusAP'] = self.AP

    def verifyTestbed(self):
        """ Loop through the testbed components and rely on components to verify themselves"""
        # Exceptions should be handled in components level
        # To be added: testbed devices not implemented as component may need to be verified, e.g
        # DHCP server, etc.
        logging.info ("Testbed %s Verifying component" % (self.testbed_info.name))
        self.AP.verify_component()
        self.Station.verify_component()
