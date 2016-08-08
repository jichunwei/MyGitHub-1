"""
   Description: 
   @author: Kevin Tan
   @contact: kevin.tann@ruckuswireless.com
   @since: June 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters:
   
   Test procedure:
    1. Config:
        -         
    2. Test:
        - Verify if the mesh tree are match with expected 
    3. Cleanup:
        -
   
   Result type: PASS/FAIL
   Results: 

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import time
import logging
import re
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components.lib.zd import wips_zd as WIPS
from RuckusAutoTest.components.lib.zd import service_zd as SERVICE

default_interval = '20' #Run a background scan on 2.4/5GHz radio every 20 seconds

class CB_ZD_WIPS_Configuration(Test):
    def config(self, conf):
        self._init_test_parameter(conf)

    def test(self):
        # After setting factory default configuration, all ZD configurations set as default
        self._verify_all_config_after_factory_default()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)

        result=self._test_background_scan_options(scan_time_2_4G=default_interval, scan_time_5G=default_interval, report_rogue=True, prevent_malicious=False)
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        #Test background scanning options
        result=self._test_background_scan_options(scan_time_2_4G='10', scan_time_5G='15', report_rogue=True, prevent_malicious=False)
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)

        #Enable WIPS 'Prevent Malicious AP' options and test it again
        WIPS.enable_wips_prevent_rogue_devices(self.zd)
        result=self._test_background_scan_options(scan_time_2_4G='25', scan_time_5G='30', report_rogue=True, prevent_malicious=True)
        if self.errmsg: 
            self.errmsg += 'after enabled Prevent Malicious AP option'
            return self.returnResult('FAIL', self.errmsg)

        #Test WIPS options
        self._test_wips_options()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _init_test_parameter(self, conf):
        self.conf = {}
        self.conf.update(conf)        
        self.errmsg = ''
        self.passmsg = ''
        
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']

    def _verify_all_config_after_factory_default(self):
        #background scanning options should be enabled both for 2.4G and 5G
        result = SERVICE.verify_background_scan_factory_setting(self.zd)
        if result:
            self.errmsg = result
            return

        #Report rogue devices is enabled and Protect the network from malicious rogue access points is disabled
        self._verify_wips_config_in_zdcli(report_rogue=True, prevent_malicious=False)
        
    def _test_background_scan_options(self, scan_time_2_4G, scan_time_5G, report_rogue, prevent_malicious):
        #only disable 2.4G options
        SERVICE.set_background_scan_options(self.zd, '', scan_time_5G)
        self._verify_background_scan_options_in_zdcli(enable_2_4G=False, scan_time_2_4G='0', enable_5G=True,scan_time_5G=scan_time_5G)
        if self.errmsg:
            return
        self._verify_wips_config_in_zdcli(report_rogue,prevent_malicious)
        if self.errmsg:
            return

        #open both 2.4G and 5G options
        SERVICE.set_background_scan_options(self.zd, option_2_4G=scan_time_2_4G, option_5G=default_interval)
        self._verify_background_scan_options_in_zdcli(enable_2_4G=True, scan_time_2_4G=scan_time_2_4G, enable_5G=True,scan_time_5G=default_interval)
        if self.errmsg:
            return
        self._verify_wips_config_in_zdcli(report_rogue,prevent_malicious)
        if self.errmsg:
            return

        #only disable 5G options
        SERVICE.set_background_scan_options(self.zd, scan_time_2_4G, '')
        self._verify_background_scan_options_in_zdcli(enable_2_4G=True, scan_time_2_4G=scan_time_2_4G, enable_5G=False,scan_time_5G='0')
        if self.errmsg:
            return
        self._verify_wips_config_in_zdcli(report_rogue,prevent_malicious)
        if self.errmsg:
            return

        #open both 2.4G and 5G options
        SERVICE.set_background_scan_options(self.zd, option_2_4G=scan_time_2_4G, option_5G=scan_time_5G)
        self._verify_background_scan_options_in_zdcli(enable_2_4G=True, scan_time_2_4G=scan_time_2_4G, enable_5G=True, scan_time_5G=scan_time_5G)
        if self.errmsg:
            return
        self._verify_wips_config_in_zdcli(report_rogue,prevent_malicious)
        if self.errmsg:
            return

        #disable both 2.4G and 5G options
        SERVICE.set_background_scan_options(self.zd, '', '')
        self._verify_background_scan_options_in_zdcli(enable_2_4G=False, scan_time_2_4G='0', enable_5G=False, scan_time_5G='0')
        if self.errmsg:
            return
        self._verify_wips_config_in_zdcli(report_rogue=False, prevent_malicious=False)
        if self.errmsg:
            return

        #reset to default value
        SERVICE.set_background_scan_options(self.zd, option_2_4G=default_interval, option_5G=default_interval)
        self._verify_wips_config_in_zdcli(report_rogue,prevent_malicious)
        if self.errmsg:
            return

    def _test_wips_options(self):
        # enable all WIPS options first
        WIPS.enable_wips_all_options(self.zd)
        self._verify_wips_config_in_zdcli(report_rogue=True,prevent_malicious=True)

        #Make sure that WIPS is automatically disabled followed by Report Rouge Devices 
        WIPS.disable_wips_report_rogue_devices(self.zd)
        self._verify_wips_config_in_zdcli(report_rogue=False,prevent_malicious=False)
        
        #Only disable prevent rogue option and enable report rouge devices 
        WIPS.enable_wips_all_options(self.zd)
        WIPS.disable_wips_prevent_rogue_devices(self.zd)
        self._verify_wips_config_in_zdcli(report_rogue=True,prevent_malicious=False)

    def _verify_wips_config_in_zdcli(self, report_rogue, prevent_malicious):
        #WIPS default options
        self.zd.navigate_to(self.zd.CONFIGURE, self.zd.CONFIGURE_WIPS)

        #Verify by ZD CLI command 'wlaninfo --system'
        info = self.zdcli.get_wlan_info_system()
        m1 = re.search(r"rogue reporting(\s*)=(\s*)(\w+)", info, re.I)
        m2 = re.search(r"malicious AP detect(\s*)=(\s*)(\w+)", info, re.I)
        if not m1 or not m2:
            self.errmsg += 'cannot find rogue reporting and malicious AP detect info'
            return
        
        if report_rogue:
            if m1.group(3).lower() != 'enabled':
                self.errmsg += "wips report rogue disabled in CLI, unexpected value"
                return
        else:
            if m1.group(3).lower() != 'disabled':
                self.errmsg += "wips report rogue enabled in CLI, unexpected value"
                return
            
        if prevent_malicious:
            if m2.group(3).lower() != 'enabled':
                self.errmsg += "wips prevent malicious rogue ap checkbox disabled in CLI, unexpected value"
                return
        else:
            if m2.group(3).lower() != 'disabled':
                self.errmsg += "wips prevent malicious rogue ap checkbox enabled in CLI, unexpected value"
                return
        
    def _verify_background_scan_options_in_zdcli(self, enable_2_4G, scan_time_2_4G, enable_5G, scan_time_5G):
        #Verify by ZD CLI command 'wlaninfo --system'
        time.sleep(2)
        info = self.zdcli.get_wlan_info_system()

        m1 = re.search(r"bg_scan_interval_for_2.4G(\s*)=(\s*)([0-9]+)(\s*)sec", info)
        if m1 is None:
            raise Exception("Unable to find bg_scan_interval_for_2.4G in cmd <wlaninfo --system>")
        if enable_2_4G:
            if m1.group(3) == '0' or m1.group(3) != scan_time_2_4G:
                self.errmsg += "2.4G scan time value %s not the same as expected %s" % (m1.group(3), scan_time_2_4G)
                return
        else:
            if m1.group(3) != '0':
                self.errmsg += "2.4G scan time value %s not the same as expected value 0" % (m1.group(3))
                return
                
        m2 = re.search(r"bg_scan_interval_for_5G(\s*)=(\s*)([0-9]+)(\s*)sec", info)
        if m2 is None:
            raise Exception("Unable to find bg_scan_interval_for_5G in cmd <wlaninfo --system>")
        if enable_5G:
            if m2.group(3) == '0' or m2.group(3) != scan_time_5G:
                self.errmsg += "5G scan time value %s not the same as expected %s" % (m1.group(3), scan_time_5G)
                return
        else:
            if m2.group(3) != '0':
                self.errmsg += "5G scan time value %s not the same as expected value 0" % (m1.group(3))
                return
        
        return
