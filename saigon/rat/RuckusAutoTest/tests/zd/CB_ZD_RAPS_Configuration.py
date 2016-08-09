"""
    Radar Avoidance Pre-scanning configuration test
    
   author: Kevin Tan
   contact: kevin.tan@ruckuswireless.com
   date: June 2013
"""

import time
import logging
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_RAPS_Configuration(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
                            }

    def config(self, conf):
        self._init_test_parameter(conf)

    def test(self):
        zd_country_code = self.zd.get_country_code()['value']
        logging.info('Country code is %s' % zd_country_code)

        raps_supported = self.zdcli.get_raps_supported_opion()
        logging.info('RAPS supported option is %s in ZD shell /writable/etc/airespider/system.xml file' % raps_supported)

        raps_option = lib.zd.service.get_radio_avoidance_prescanning_option(self.zd)
        logging.info('RAPS option in ZD GUI:%s' % raps_option)

        raps_cli = lib.zdcli.service.get_service_info(self.zdcli)
        logging.info('RAPS option in ZD CLI:\n%s' % raps_cli)

        if raps_supported == True:
            logging.info('Verify RAPs option in ZDCLI and ZD GUI, and verify AP scand option in AP CLI and scand process in AP shell')

            if raps_option != 'enable':
                return self.returnResult('FAIL', 'RAPS is supported in country code %s and RAPS checkbox %s in ZD GUI' % (zd_country_code, raps_option))
            
            if raps_cli.get('RAPS').lower() != 'enabled':
                return self.returnResult('FAIL', 'RAPS is supported in country code %s and RAPS CLI is grey in ZD GUI' % zd_country_code)
            
            self.verify_ap_scand(True)

            #Verify after set ZD RAPS disabled
            logging.info('Set RAPS option to disable in ZF GUI and check it in ZD CLI, AP CLI and AP shell')
            lib.zd.service.set_radio_avoidance_prescanning_option(self.zd, False)
            self.verify_zd_cli('disabled')
            self.verify_ap_scand(False)

            #Verify after set ZD RAPS enabled
            logging.info('Set RAPS option to enable in ZF CLI and check it in ZD GUI, AP CLI and AP shell')
            lib.zdcli.service.configure_service(self.zdcli, {'raps':True})
            self.verify_zd_cli('enabled')
            self.verify_zd_gui(True)
            self.verify_ap_scand(True)

            #Verify after set AP option False
            logging.info('Set RAPS option to enable in AP CLI and check it in AP shell')
            self.active_ap.set_scand_option(False)
            self.verify_ap_scand(False)
            self.active_ap.set_scand_option(True)
            self.verify_ap_scand(True)
        else:
            if raps_option != 'checkbox_grey':
                return self.returnResult('FAIL', 'RAPS is not supported in country code %s and RAPS checkbox[%s] is not grey in ZD GUI' 
                                         % (zd_country_code, raps_option))

        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self.passmsg = 'Radar Avoidance Pre-scanning configuration test successfully'
        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _init_test_parameter(self, conf):
        self.conf = {}
        self.conf.update(conf)        
        
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.active_ap   = self.carrierbag[self.conf['ap_tag']]['ap_ins']

        self.errmsg = ''
        self.passmsg = ''
        
    def verify_ap_scand(self, enable_option):
        ap_scand_option = self.active_ap.get_scand_option()
        ap_scand_process = self.active_ap.grep_ap_process('scand')

        if enable_option is True:
            if ap_scand_option is False :
                self.errmsg += 'scand is enabled in AP but get scand option disabled'
    
            if ap_scand_process is False :
                self.errmsg += 'scand is enabled in AP but get scand process in AP shell disabled'
        else:
            if ap_scand_option is True :
                self.errmsg += 'scand is disabled in AP but get scand option enabled'
    
            if ap_scand_process is True :
                self.errmsg += 'scand is disabled in AP but get scand process in AP shell enabled'

    def verify_zd_gui(self, enable_option):
        raps = lib.zd.service.get_radio_avoidance_prescanning_option(self.zd)
        #@author:chen.tao since:2013-10-28 to correct the logical error
        raps_status = True if raps == 'enable' else False
        if raps_status != enable_option:
        #@author:chen.tao since:2013-10-28 to correct the logical error
        
        #@author:chen.tao since:2013-10-28 to add the missing "%s" after "should be" 
            self.errmsg = 'RAPS is %s in ZD GUI, should be %s' % (raps, enable_option)
        #@author:chen.tao since:2013-10-28 to add the missing "%s" after "should be" 
    def verify_zd_cli(self, enable_option):
        cli = lib.zdcli.service.get_service_info(self.zdcli)
        raps = cli.get('RAPS').lower()

        if raps != enable_option:
            self.errmsg = 'RAPS is %s in ZD GUI, should be %s' % (raps, enable_option)
