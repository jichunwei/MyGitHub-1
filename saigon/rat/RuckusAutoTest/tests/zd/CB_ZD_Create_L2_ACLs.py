# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module doc string is accurate since it will be used in report generation.

"""Description:

    Prerequisite (Assumptions about the state of the testbed/DUT):

    Required components:
    Test parameters:
    Result type: PASS/FAIL
    Results: PASS
             FAIL otherwise

    Messages:
        - If PASS,
        - If FAIL, prints out the reason for failure

    Test procedure:
    1. Config:
        -
    2. Test:
        -
    3. Cleanup:
        -

    How is it tested: (to be completed by test code developer)

"""
import logging
import time

from RuckusAutoTest.models import Test

class CB_ZD_Create_L2_ACLs(Test):
    required_components = []
    parameter_description = {"num_of_acl_entries":"",                             
                             "num_of_mac":1,                             
                             "target_station":"ip addr of target station",
                             'acl_name_list':[]}
        
    def config(self, conf):        
        self._initTestParameters(conf)
        
    
    def test(self):
#        self.acl_name_list = []
        self.acl_mac_list = []
        if not self.acl_name_list:
            for i in range(self.num_of_acl_entries):
                acl_name = "Test_ACLs_%d" % i
                self.acl_name_list.append(acl_name)
                    
        gen_mac_list = self._generate_mac_addr(self.conf['num_of_mac'])
        if not gen_mac_list.__contains__(self.sta_wifi_mac_addr):
            gen_mac_list.append(self.sta_wifi_mac_addr)
            
        self.acl_mac_list = gen_mac_list
            

        logging.info("Create %d ACL rules on the Zone Director" % len(self.acl_name_list))
        msg = "Each ACL has name prefix ---- Test_max_ACLs; policy ----- \'allow-all\'; "
        msg += "restricted mac addr ----- %s" % self.acl_mac_list
        logging.info(msg)
        
        init_acl_name = self.acl_name_list[0]
        
        self.zd.create_acl_rule([init_acl_name], self.acl_mac_list, True)
        
        for index in range(1, len(self.acl_name_list)):
            acl_name = self.acl_name_list[index]
            self.zd.clone_acl_rule(init_acl_name, new_acl_name = acl_name)
                    
        self._update_carrier_bag()
        
        return ("PASS", "ACL create successfully, acl_name_list[%s]" % self.acl_name_list)
        
                           
    def oncleanup(self):
        pass
    
    def _initTestParameters(self, conf):
        self.conf = {'num_of_acl_entries': 1,
                     'target_station':'192.168.1.11',
                     'num_of_mac':127,
                     'acl_name_list':[]
                    }
        
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        if 'active_zd' in self.carrierbag:
            self.zd = self.carrierbag['active_zd']
        
        self.ping_timeout = 150
        self.check_status_timeout = 120                
        self.num_of_acl_entries = self.conf['num_of_acl_entries']
        self.sta_wifi_mac_addr = self._get_sta_wifi_mac_addr(self.conf)
        self.acl_name_list = self.conf['acl_name_list']
        logging.info("wifi mac address[%s]" % self.sta_wifi_mac_addr)
                                        
        self.errmsg = ''
        self.passmsg = ''

    def _update_carrier_bag(self):
        self.carrierbag['existed_acl_name_list'] = self.acl_name_list
        self.carrierbag['existed_num_of_acl_entries'] = self.num_of_acl_entries
        self.carrierbag['existed_acl_mac_list'] = self.acl_mac_list
    
    def _generate_mac_addr(self, num=128):
        mac_list = []
        for i in range(num):            
            mac = [0, 0, 0, 0, 0, i+1]
            mac = ':'.join(map(lambda x: "%02x" % x, mac))
#            if not mac_list.__contains__(mac):
            mac_list.append(mac)
                
        return mac_list

    def _get_sta_wifi_mac_addr(self, conf):
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
    
    def _verify_acl_list_on_webui(self):
        
        created_acl_list = self.testbed.components['ZoneDirector'].get_all_acl_names()
        if len(created_acl_list) != len(self.acl_name_list):
            logging.debug("The maximum number of ACLs must be created: %d" % len(self.acl_name_list))
            logging.debug("The maximum number of ACLs shown on the ZD: %d" % len(created_acl_list))
            return ["FAIL", "The total of ACL rules  is not correct"]

        # Verify that name of each ACL created correctly
        for acl_name in self.acl_name_list:
            if not acl_name in created_acl_list:
                return ["FAIL", "The ACL %s is not shown on the ZD" % acl_name]
        logging.info("Create %d ACLs on the ZD successfully" % len(self.acl_name_list))
                    
    