'''
Description:

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector', 'RuckusAP'
   Test parameters: 
   Result type: PASS/FAIL
   Results: PASS:
            FAIL:  

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - 
   2. Test:
       -            
   3. Cleanup:
       - 
    How it was tested:
        
        
Create on 2013-5-17
@author: cwang@ruckuswireless.com
'''

import logging
from xml.dom import minidom
import re
import traceback

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector

from RuckusAutoTest.components import Helpers

class CB_ZD_CLI_Test_AP_CountryCode(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(cc='BH',
                         ccalias='Bahrain',
                         ap_tag = 'AP_01'
                         )
        self.conf.update(conf)
        logging.info('Load test configuration')
#        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.cc = self.conf.get('cc')
        self.ccalias = self.conf.get('ccalias')
        self.ap_tag = self.conf.get('ap_tag')
        self.mac_addr = self.testbed.get_aps_sym_dict()[self.ap_tag]['mac']
        logging.info('Load test configuration DONE.')
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        logging.info('cat countrycode informaiton from country-list.xml')
        logging.info('countrycode:%s' % self.cc)
        try:
            data = self.zdcli.do_shell_cmd("cat /etc/airespider-default/country-list.xml | grep %s" % self.cc)
        except Exception, e:                        
            logging.debug(traceback.format_exc())
            return self.returnResult('FAIL', e.message)
        
        try:        
            (cc, ccalias, an, bgn) = self._parse_country_code(data)
            if ccalias != self.ccalias:
                return self.returnResult('FAIL', "expected countrycode alias:%s, actual %s" % 
                                         (self.ccalias, ccalias))
            
            _cfg = {}
            _cfg['A/N'] = an
            _cfg['B/G/N'] = bgn
            msg = self._test_channel_range(_cfg)
            if msg:
                return self.returnResult('FAIL', msg)
            else:
                return self.returnResult('PASS', 
                                         'The Countrycode %s testing is PASS' % self.cc)  
            
        except Exception, e:
            logging.debug(traceback.format_exc())
            return self.returnResult('FAIL', e.message)
        
          
        
        return self.returnResult('PASS', 'Country Code %s Testing Pass' % self.ccalias)
    
    def cleanup(self):
        self._update_carribag()
        

    def _test_channel_range(self, expected_cfg = None):
        logging.info('Get channel range from ZDCLI.')
        # 'Channel Range': {'A/N': '36,40,44,48,149,153,157,161 (Disallowed= )','B/G/N': '1,2,3,4,5,6,7,8,9,10,11 (Disallowed= )'},
        apinfo = Helpers.zdcli.configure_ap.get_ap(self.zdcli, 
                                                   self.mac_addr)
        cr_zdcli = apinfo['Channel Range']
        an = cr_zdcli.get('A/N', None)
        if an:
            an = an.split()[0]
            
        bgn = cr_zdcli.get('B/G/N', None)
        if bgn:
            bgn = bgn.split()[0]
                                   
        if an not in expected_cfg['A/N']:
            return "Expected %s, actual %s" % (expected_cfg['A/N'], an)
        
        if bgn != expected_cfg['B/G/N']:
            return "Expected %s, actual %s" % (expected_cfg['B/G/N'], bgn)
        
        return None
            
    
    def _parse_country_code(self, data):
        """
        data = <country id="4" 
        name="BH" 
        full-name="Bahrain" 
        code="48" 
        channels-11bg="1,2,3,4,5,6,7,8,9,10,11,12,13" 
        channels-11a="36,40,44,48,52,56,60,64,149,153,157,161,165" 
        dfs-channels-11a="" 
        centrino-channels-11a=""  
        allow-dfs-channels="false" 
        allow-dfs-models="" 
        allow-11ng-40="true" 
        allow-11na-40="true" 
        channels-11ng-20="1,2,3,4,5,6,7,8,9,10,11,12,13" 
        channels-11ng-40="1,2,3,4,5,6,7,8,9,10,11,12,13" 
        cband-channels-11a="" 
        allow-cband-channels="false" 
        channels-indoor-block="0" />
        return:
            name, 
            full-name, 
            channels-11a, 
            channels-11bg, 
#            channels-11ng-20, 
#            channels-11ng-40
        """
        node = minidom.parseString(data)
        cc = node.getElementsByTagName('country')[0]        
        return (cc.getAttribute("name"),
                cc.getAttribute("full-name"),
                cc.getAttribute("channels-11a"),
                cc.getAttribute("channels-11bg"),
                )

        
    