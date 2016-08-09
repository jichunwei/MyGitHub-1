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
        
        
Create on 2011-8-11
@author: cwang@ruckuswireless.com
'''

import logging
import re
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector
from RuckusAutoTest.common import Ratutils as utils


class CB_ZD_Hotspot_Walled_Garden(Test):
    required_components = ['ZoneDirector', 'ZoneDirectorCLI', 'RuckusAP']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(ap_tag = 'tap',
                         check_wlan_timeout = 45,
                         wlan_cfg = dict(ssid = "RAT-Open-None", auth = "open", encryption = "none", 
                                         type="hotspot", hotspot_profile = 'A Sampe Hotspot Profile'),
                         hotspot_cfg = None,
                        )
        self.wlan_id = None
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.zd_cli = self.testbed.components['ZoneDirectorCLI']
        self._retrieve_carribag()
        self.errmsg = ''
        self.msg = ''
                
    
    def _retrieve_carribag(self):        
        self.active_ap = self.carrierbag.get(self.conf['ap_tag'])['ap_ins']         
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
        self._get_dns()
             
    
    def test(self):
        self._testACLOnZDLinuxShell()
        if self.errmsg: return self.returnResult("FAIL", self.errmsg)
        self._testACLOnAPLinuxShell()
        if self.errmsg: return self.returnResult("FAIL", self.errmsg)   
        
        return self.returnResult('PASS', 'Walled garden testing')     
    
    def cleanup(self):
        self._update_carribag()


    def _testACLOnZDLinuxShell(self):        
        logging.info("Verify the Redirect Policy stored in the ZD's Linux shell "
                     "in /proc/afmod/policy")
        time.sleep(20)
        if not self.wlan_id:
            cnt = 5
            while cnt:
                try:
                    self.wlan_id = self.zd_cli.get_wlan_id(self.conf['wlan_cfg']['ssid'])
                    break
                except:
                    cnt -= 1
                    

        acl_list = self.zd_cli.get_hotspot_policy(self.wlan_id, redir_policy = True)

        for entry in self.conf['hotspot_cfg']['walled_garden_list']:
            logging.info("Verify entry [%s]" % entry)
            #Updated by Jacky Luh @since: 2013-12-05
            #9.8 build enhance the walled garden policy file to surpport the domain name
            ip, port, mask = self._parseWalledGardenEntry(entry, resolve_name = False)
            logging.info("IP:[%s] - port[%s] - mask[%s]" % (ip, port, mask))
            if mask:
                dst_addr = "%s/%s" % (ip, mask)
            else:
                dst_addr = "%s" %ip
            t1 = time.time()
            duration = 0
            while True:
                timedout = duration > self.conf['check_wlan_timeout']
                match = [acl for acl in acl_list if acl['dst-addr'] == dst_addr]
                if not match and not timedout:
                    time.sleep(5)
                    acl_list = self.zd_cli.get_hotspot_policy(self.wlan_id,
                                                              redir_policy = True)

                else:
                    break

                duration = time.time() - t1

            logging.info("It took %s seconds for the ZD to apply "
                         "the entry [%s]" % (duration, entry))
            if not match:
                self.errmsg = "Not found in the ZD's Linux shell an "\
                              "ACL entry for the walled garden entry [%s]" % entry
                return

            if match[0]['action'] != "Pass":
                self.errmsg = "The ACL entry [%s] has the action [%s] " \
                              "instead of [Pass]" % (entry, match[0]['action'])
                return

            if port and match[0]['dport'] != port:
                self.errmsg = "The ACL entry [%s] has the port [%s] " \
                              "instead of [%s]" % (entry, match[0]['dport'], port)
                return

    #JLIN@20100611 modified for comparing restricted_subnet logical error
    def _testACLOnAPLinuxShell(self):
        # Verify if the ACL has been applied in the AP's Linux shell
        # This test is performed when the walled garden
        # targets are configured
        ap_list = [self.active_ap]
        for ap in ap_list:
            logging.info("Verify the Redirect Policy list stored in "\
                         "the AP[%s]'s Linux shell in /proc/afmod/policy" % \
                         ap.base_mac_addr)

            acl_list = ap.get_hotspot_policy(self.wlan_id,
                                             redir_policy = True)

            for entry in self.conf['hotspot_cfg']['walled_garden_list']:                                    
                logging.info("Verify entry [%s]" % entry)
                #Updated by Jacky Luh @since: 2013-12-05
                #9.8 build enhance the walled garden policy file to surpport the domain name
                ip, port, mask = self._parseWalledGardenEntry(entry, resolve_name = False)
                logging.info("IP:[%s] port[%s] - mask[%s]" % (ip, port, mask))
                #@author: liangaihua,@since: 2015-4-10,@change: 9.12 later version not support mask for domain name
                #***************
                if not mask:
                    mask = "32"
                dst_addr = "%s/%s" % (ip, mask)
                #*******************************************
                match = [acl for acl in acl_list if acl['dst-addr'] == dst_addr]
                if not match:
                    self.errmsg = "Not found in the AP's Linux shell "\
                                  "an ACL entry for the walled garden entry [%s]" % entry
                    return

                if match[0]['action'] != "Pass":
                    self.errmsg = "The ACL entry [%s] has the action [%s] "\
                                  "instead of [Pass]" % (entry, match[0]['action'])
                    return

                if port and match[0]['dport'] != port:
                    self.errmsg = "The ACL entry [%s] has the port [%s] "\
                                  "instead of [%s]" % (entry, match[0]['dport'], port)
                    return

        self.msg += "All the walled garden entries have been applied on the AP successfully. "  
        
        
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
            name = ip
            ip = utils.lookup_domain_name(ip, self.dns_server_addr)
            logging.info('[%s] -> [%s]' % (name, ip))
        #@author: liang aihua,@since:2015-7-13,@change: keep same with different versions  
        if self.zd.version['release']in ['9.12.0.0','9.10.1.0']:
            if not mask:
                mask = "32"
        else:
            
            #@author: liang aihua,@since:2015-4-9,@change: no mask when walled garden is domain name.
            #**********************
            if ip_re.match(ip):
                if not mask:
                    mask = "32"
            #*************************************

        return (ip, port, mask)   
    
    def _get_dns(self):        
        logging.info("Get the DNS server address configured on the ZD")
        zd_ip_cfg = self.zd.get_ip_cfg()
        if not zd_ip_cfg['pri_dns']:
            msg = "The ZD does not have information of the DNS server. "\
                  "It cannot resolve names in walled garden entries."
            raise Exception(msg)
        self.dns_server_addr = zd_ip_cfg['pri_dns']           