'''
Created on Feb 15, 2011
@author: cwang@ruckuswireless.com
'''

import logging
import random
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import l2_acl_cli
#from RuckusAutoTest.components import Helper_ZD as zhlp
from RuckusAutoTest.common import Ratutils as utils


class CB_Scaling_ZD_CLI_Create_L2_ACLs(Test):
    '''
    Create L2 ACLs including in-depth configurations against ZDCLI.
    '''    
    def config(self, conf):
        self.init_param(conf)
    
    def test(self):        
        l2_acl_cli.create_l2acl(self.zdcli, self.l2acl_cfg)         
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self.update_carribag()
        return self.returnResult('PASS', self.passmsg)
            
        
    def cleanup(self):
        pass
    
    def init_param(self, conf):
        self.conf = dict(num_of_acl=32,
                         num_of_mac=127,
                         target_station= None#getting WIFI mac addr
                         )        
        self.conf.update(conf)
        self.l2acl_cfg = self.get_l2acl_conf_list(self.conf['num_of_acl'], self.conf['num_of_mac'])
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''
    
    def retrive_carribag(self):
        pass
    
    
    def update_carribag(self):
        pass
    
    
    def generate_mac_addr(self, num=128):
        mac_list = []
        for i in range(num):            
            mac = [0, 0, 0, 0, 0, i+1]
            mac = ':'.join(map(lambda x: "%02x" % x, mac))
            mac_list.append(mac)
                
        return mac_list
        
    def get_l2acl_conf_list(self, num_of_acl=32, num_of_mac=127):
        l2acl_conf_list = []
        mac_list = self.generate_mac_addr(num_of_mac)
        if self.conf.has_key('target_station') and self.conf['target_station']:
            mac_list.append(self.get_sta_wifi_mac_addr(self.conf))
        
        for i in range(num_of_acl):
            acl_name = "Test_ACLs_%d" % i
            l2acl_conf_list.append(dict(
                                    acl_name = acl_name,
                                    description = utils.make_random_string(random.randint(2,32),type = 'alnum'),
                                    mac_entries =mac_list,
                                    policy = 'allow',
                                    ))
        
        return l2acl_conf_list  

    
    def get_sta_wifi_mac_addr(self, conf):
        for station in self.testbed.components['Station']:
            if station.get_ip_addr() == conf['target_station']:
                # Found the target station
                self.target_station = station
                logging.info("Remove all WLAN profiles on the target station %s" % self.target_station.get_ip_addr())
                self.target_station.remove_all_wlan()
                logging.info("Make sure the target station %s disconnects from wireless network" % 
                             self.target_station.get_ip_addr())
                start_time = time.time()
                while True:
                    if self.target_station.get_current_status() == "disconnected":
                        break
                    time.sleep(1)
                    if time.time() - start_time > self.check_status_timeout:
                        raise Exception("The station did not disconnect from wireless network within %d seconds" % 
                                        self.check_status_timeout)
                logging.info("Renew IP address of the wireless adapter on the target station")
                self.target_station.renew_wifi_ip_address()
                break
        if not self.target_station:
            raise Exception("Target station %s not found" % conf['target_station'])

        # Get mac address of wireless adapter on the target station.
        # This address is used as the restricted mac address in an ACL rule
        sta_wifi_ip_addr = None
        sta_wifi_mac_addr = None
        try:
            sta_wifi_ip_addr, sta_wifi_mac_addr = self.target_station.get_wifi_addresses()
            
        except:
            raise Exception("Unable to get MAC address of the wireless adapter of the target station %s" % 
                                self.target_station.get_ip_addr())
        
        return sta_wifi_mac_addr    