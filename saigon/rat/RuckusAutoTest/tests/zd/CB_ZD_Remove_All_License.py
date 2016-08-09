"""
Description: ZD_ImportLicense test class tests the operations related to temporary/permanent licenses
"""
import logging

from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.ZoneDirectorCLI import ZoneDirectorCLI

class CB_ZD_Remove_All_License(Test):
    
    def config(self, conf):
        self._init_test_params(conf)
    
    def test(self):
        self._cfg_remove_all_licenses()
        self._cfg_set_expiration_ratio("1x")
        self._cfg_restore_serial_number()   
    
    def cleanup(self):
        pass
           
    def _cfg_remove_temporary_licenses(self):
        logging.info("Try to remove any existing temporary licenses")
        lib.zd.lic.remove_temporary_license(self.zd)

    def _cfg_remove_permanent_licenses(self):
        logging.info("Try to remove any existing permanent licenses")
        lib.zd.lic.remove_all_permanent_licenses(self.zd)

    def _cfg_remove_all_licenses(self):
        self._cfg_remove_temporary_licenses()
        self._cfg_remove_permanent_licenses()
        
    def _cfg_restore_serial_number(self):
        if self.zdsn:
            logging.info("Restore the serial number of the ZD to %s" % self.zdsn)
            self.zdcli.set_serial_number(self.zdsn)

    def _cfg_set_expiration_ratio(self, ratio):
        if self.conf['testcase'] == 'temp-license-expiration':
            logging.info("Set the license expiration ratio to %s" % ratio)
            lib.zd.lic.set_expiration_ratio(self.zd, ratio)
            
    def _init_test_params(self, conf):
        self.conf = conf
        self.zd = self.testbed.components['ZoneDirector']  
        zd_cli_cfg = {'ip_addr':self.zd.ip_addr, 'username':self.zd.username, 'password':self.zd.password}
        self.zdcli = ZoneDirectorCLI(zd_cli_cfg)        
    
    def _retrive_carrier_bag(self):
        self.zdsn = self.carrierbag["exited_zdsn"]
        if self.carrierbag.has_key("testcase"):
            self.conf['testcase'] = self.carrierbag['testcase']
    