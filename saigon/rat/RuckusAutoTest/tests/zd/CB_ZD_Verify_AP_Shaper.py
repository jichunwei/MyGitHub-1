"""
Description: 

   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Sep 2011

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP'
   Test parameters:
    - rate_limit: Rate limit of uplink/downlink
    - link_type: uplink or downlink, the value is "up" or "down"
    - ap_tag: Access Point tag
    - ssid: wlan ssid
    
    Test procedure:
    1. Config:
        - initilize test parameters: get rate limit in mbps, and rate_limit_w_error_mbps.         
    2. Test:
        - Get shaper information from AP for uplink/downlink
        - Verify shaper is same as rate limit.  
    3. Cleanup:
        - N/A
    
   Result type: PASS/FAIL
   Results: PASS: if shaper information in AP of uplink/downlink is same as rate limit.
            FAIL: if can't get shaper information or shaper value is incorrect.

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

"""

import logging
import re

from RuckusAutoTest.models import Test

class CB_ZD_Verify_AP_Shaper(Test):
    required_components = ['RuckusAP']
    parameter_description = {'rate_limit': 'Rate limit',
                             'link_type': 'Up or down link',
                             'ap_tag': 'ap tag',
                             'ssid': 'wlan ssid'}

    def config(self, conf):
        self.conf = dict(rate_limit='0.25mbps',
                         link_type='up',
                         ap_tag='aptag',
                         ssid='')
        
        self.conf.update(conf)
        
        self.rate_limit_kbps = self._get_rate_limit_value_kbps(self.conf['rate_limit'])
        self.errmsg = ""
        self.passmsg = ""
        
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.active_ap_mac = self.active_ap.get_base_mac()

    def test(self):
        logging.info('Verify AP shaper is same as expected.')
        
        try:
            ap_shaper = self.active_ap.get_shaper(self.conf['ssid'])
            if self.conf['link_type'].lower() == 'up':
                ap_shaper_value = ap_shaper['up']
            else:
                ap_shaper_value = ap_shaper['down']
                
            if ap_shaper_value:
                ap_shaper_obj = re.match(r"(\d+)", ap_shaper_value)
                
                logging.info("Verify the Shaper[%s] is %s in ActiveAP[%s]" % \
                                (self.conf['link_type'], ap_shaper_value, self.active_ap_mac))
                
                if ap_shaper_obj.group(1) != str(self.rate_limit_kbps):
                    msg = "The shaper[%s] setting is %s instead of %s in AP[%s]" % \
                           (self.conf['link_type'], ap_shaper_value, self.rate_limit_kbps, self.active_ap_mac)
                    logging.info(msg)            
                    self.errmsg = msg
            else:
                if self.rate_limit_kbps != 0:
                    self.errmsg = "Didn't get %slink shaper values." % (self.conf['link_type'])
            
            self.passmsg = 'The shaper[%s] is correct in ActiveAP[%s].' % (self.conf['link_type'], self.active_ap_mac)
                
        except Exception, ex:
            self.errmsg = ex.message
            
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult("PASS", self.passmsg)

    def cleanup(self):
        pass
    
    def _get_rate_limit_value_kbps(self, rate_limit):
        rate_obj = re.match(r"([0-9\.]+)\s*(mbps)", rate_limit, re.I)
        if not rate_obj:
            if rate_limit.lower() != 'disabled':
                raise Exception("Invalid rate limit value (%s)" % rate_limit)
            else:
                return 0

        rate_limit_kbps = int(float(rate_obj.group(1)) * 1000)
        
        return rate_limit_kbps