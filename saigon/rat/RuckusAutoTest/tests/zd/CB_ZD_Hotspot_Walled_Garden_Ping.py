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
        
        
Create on 2011-8-12
@author: cwang@ruckuswireless.com
'''

import logging
import re

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod


class CB_ZD_Hotspot_Walled_Garden_Ping(Test):
    required_components = []
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(ping_timeout_ms = 5000,
                         walled_garden_list = None,
                         sta_tag = 'sta_1'
                         )
        self.zd = self.testbed.components['ZoneDirector']
        self.conf.update(conf)        
        self._retrieve_carribag()
        self.errmsg = ''
        self.msg = ''
    
    def _retrieve_carribag(self):
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
        self._get_dns()
    
    def test(self):        
        for entry in self.conf['walled_garden_list']:
            ip, port, mask = self._parseWalledGardenEntry(entry, resolve_name = False)
            if mask == "32":
                logging.info("The walled garden destination: %s" % ip)
                self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, ip,
                                                                  ping_timeout_ms = self.conf['ping_timeout_ms'])
                if self.errmsg:
                    return self.returnResult('FAIL', self.errmsg)
                
        return self.returnResult('PASS', "The station could transmit traffic to destinations in the walled garden list. ")        
    
    def cleanup(self):
        self._update_carribag()
        
        
    def _parseWalledGardenEntry(self, subnet, resolve_name = True):
        entry_re = re.compile("^([\w\-\.]+):?([\d]*)/?([\d]*)$")
        ip_re = re.compile("^[\d\.]+$")
        m = entry_re.match(subnet)
        if m:
            ip = m.group(1)
            port = m.group(2)
            mask = m.group(3)

        else:
            raise Exception("Invalid walled garden entry [%s]" % subnet)

        if not ip_re.match(ip) and resolve_name:
            ip = utils.lookup_domain_name(ip, self.dns_server_addr)

        if not mask:
            mask = "32"

        return (ip, port, mask)  
    

    def _get_dns(self):
        logging.info("Get the DNS server address configured on the ZD")
        zd_ip_cfg = self.zd.get_ip_cfg()
        if not zd_ip_cfg['pri_dns']:
            msg = "The ZD does not have information of the DNS server. "\
                  "It cannot resolve names in walled garden entries."
            raise Exception(msg)
        self.dns_server_addr = zd_ip_cfg['pri_dns']      