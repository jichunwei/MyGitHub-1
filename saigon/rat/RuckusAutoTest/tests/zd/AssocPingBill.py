# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.
"""
AssocPingBill Test class tests the ability of a station to associate with an AP with a given security configuration.
The ability to associate is confirmed via a ping test.
"""

import os

from RuckusAutoTest.models import Test


# Note that the name of the Test class must match the name of this file for ease of runtime-reference

def ping(target_ip, tries = 1, timeout_ms = 300):
    '''
    ping performs a basic connectivity test to the specified target
    Returns 1 on error and 0 if any of the tries were successful
    '''
    cmd = "ping %s -n 1 -w %d > NUL" % (target_ip, timeout_ms)
    for i in range(tries):
        err = os.system(cmd)
        if not err:
            return 0 # reachable 
    return 1         # error -- unreachable after 'tries' ping attempts


class AssocPingBill(Test):
    """
    AssocPingBill Test class tests the ability of a station to associate with an AP with a given security configuration.
    The ability to associate is confirmed via a ping test.
    """
    required_components = ['Station', 'AP']
    parameter_description = {'timeout':    'Maximum length of time in seconds to wait for association and ping to complete',
                           'ip':         'IP address to Ping',
                           'wlan_cfg':   'dictionary of association parameters (e.g. Station Config() interface)'}

    def config(self, conf):
        self.timeout = int(conf['timeout'])
        self.ip_addr = conf['ip']
        self.testbed.Station.cfg_wlan(conf['wlan_cfg'])
    def test(self):
        # This method isn't completely correct as written since it doesn't acount
        # for the OS overhead time to run the ping command.
        # This should be re-written to track actual elapsed time
        for sec in range(self.timeout + 1):
            err = ping(self.ip_addr, tries = 1, timeout_ms = 1000)
            if not err:
                return "PASS", "%2s" % sec
        return "FAIL", "timeout exceeded" 
    def cleanup(self):
        self.testbed.Station.WiFiUnconfig()

