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
import libZD_TestConfig as tconfig
from RuckusAutoTest.components import Helpers

class CB_ZD_Verify_L2_ACLs(Test):
    
    required_components = []
    parameter_description = {'target_station'  :'ip address of target station',
                             'ip'             :'ip address to ping',
                             'wlan_cfg_list': 'wlan of list'}
        
    def config(self, conf):
        
        self._initTestParameters(conf)
        self._retrive_carrier_bag()
        self.sta_wifi_mac_addr = self._get_sta_wifi_mac_addr(conf)
                     
    def test(self):
#        import pdb
#        pdb.set_trace()
#        self._bind_acl_2_wlan()        
        index = 0
        logging.info("Make sure that the created ACLs operate well by trying with the first ACL in the ACL table")
        msg = "The first ACL information: acl_name ----- %s; policy ----- \'allow-all\'; " % self.acl_name_list[index]
        msg += "mac address in ACL ----- %s" % self.sta_wifi_mac_addr
        logging.info(msg)
        
#        self.testbed.components['ZoneDirector'].remove_all_wlan()
        self._remove_wlansOnStation()        
        self.wlan_cfg = self.wlan_cfg_set[index]
        result, msg = self._verify_acl_functionality(self.acl_name_list[index])
        if result == "FAIL":
            return (result, msg)
        index = self.num_of_acl_entries/2
        logging.info("Make sure that the created ACLs operate well by trying with the 500th ACL in the ACL table")
        msg = "The 500th ACL information: acl_name ----- %s; policy ----- \'allow-all\'; " % self.acl_name_list[index]
        msg += "mac address in ACL ----- %s" % self.sta_wifi_mac_addr
        logging.info(msg)
#        self.testbed.components['ZoneDirector'].remove_all_wlan()
#        self.wlan_cfg = self.wlan_cfg_set[index]
        self._remove_wlansOnStation()
#        import pdb
#        pdb.set_trace()
        result, msg = self._verify_acl_functionality(self.acl_name_list[index])
        if result == "FAIL":
            return (result, msg)
        
        logging.info("Make sure that the created ACLs operate well by trying with the last ACL in the ACL table")
        msg = "The last ACL information: acl_name ----- %s; policy ----- \'allow-all\'; " % self.acl_name_list[-1]
        msg += "mac address in ACL ----- %s" % self.sta_wifi_mac_addr
        logging.info(msg)
#        self.testbed.components['ZoneDirector'].remove_all_wlan()
#        self.wlan_cfg = self.wlan_cfg_set[index]
        self._remove_wlansOnStation()
#        import pdb
#        pdb.set_trace()        
        result, msg = self._verify_acl_functionality(self.acl_name_list[-1])
        if result == "FAIL":
            return self.returnResult('FAIL', msg)
        
        return self.returnResult('PASS', 'Maximum ACLs + Maximum WLANs checked successfully')
    
    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'target_station':'192.168.1.11',
                     'ip'             :'ip address to ping',
                     'wlan_cfg_list': None
                    }
        self.conf.update(conf)
        
        self.wlan_cfg_set = None
        if not self.conf['wlan_cfg_list']:            
            self.wlan_cfg_set = tconfig.get_wlan_profile('set_of_32_open_none_wlans')
        else:
            self.wlan_cfg_set = self.conf['wlan_cfg_list']
            
        self.ip_addr = conf['ip']        
        
        self.zd = self.testbed.components['ZoneDirector']
        
        self.ping_timeout = 150
        self.check_status_timeout = 120
        self.target_station = None
                            
        self.errmsg = ''
        self.passmsg = ''
        
    def _bind_acl_2_wlan(self, ):
        index = 0        
        for w_cfg in self.wlan_cfg_set:            
            acl_name = self.acl_name_list[index]
            w_cfg['acl_name'] = acl_name  
            Helpers.zd.wlan.edit_wlan(self.zd, w_cfg['ssid'], w_cfg)
            index += 1
    
    def _remove_wlansOnStation(self):
        """
        Remove all wlan profiles on the remove station, and verify its status to make sure that it completely
        disconnects from the wireless networks
        """
        logging.info("Remove all WLAN profiles on the remote station")
        self.target_station.remove_all_wlan()

        logging.info("Make sure the target station disconnects from the wireless networks")
        start_time = time.time()
        while True:
            if self.target_station.get_current_status() == "disconnected":
                break
            time.sleep(1)
            if time.time() - start_time > self.check_status_timeout:
                raise Exception("The station did not disconnect from wireless network within %d seconds" % 
                                self.check_status_timeout)
                
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
    
    def _verify_associated_client(self):
        """
        Verify information of target station when it associate to the wlan successfully
        """
        logging.info("The station is in the allowed list of ACL, make sure it can associate to the WLAN")
        start_time = time.time()
        while True:
            if self.target_station.get_current_status() == "connected":
                logging.info("The target station is connected to the ZD now")
                break
            time.sleep(1)
            if time.time() - start_time > self.check_status_timeout:
                return ["FAIL", "The target station does not associate to the wireless network after %d seconds" % 
                        self.check_status_timeout]

        logging.info("Get IP and MAC addresses of the wireless adapter on the target station %s" % 
                     self.target_station.get_ip_addr())
        start_time = time.time()
        sta_wifi_ip_addr = None
        sta_wifi_mac_addr = None
        while time.time() - start_time < self.check_status_timeout:
            sta_wifi_ip_addr, sta_wifi_mac_addr = self.target_station.get_wifi_addresses()
            if sta_wifi_mac_addr and sta_wifi_ip_addr and sta_wifi_ip_addr != "0.0.0.0" and not sta_wifi_ip_addr.startswith("169"):
                break
            time.sleep(1)

        if not sta_wifi_mac_addr:
            raise Exception("Unable to get MAC address of the wireless adapter of the target station %s" % 
                            self.target_station.get_ip_addr())
        elif not sta_wifi_ip_addr:
            raise Exception("Unable to get IP address of the wireless adapter of the target station %s" % 
                            self.target_station.get_ip_addr())
        elif sta_wifi_ip_addr == "0.0.0.0" or sta_wifi_ip_addr.startswith("169"):
            raise Exception("The target station %s could not get IP address from DHCP server" % 
                            self.target_station.get_ip_addr())

        logging.info("Verify information of the target station shown on the Zone Director")
        client_info_on_zd = None
        status_verifying_count = 5
        start_time = time.time()
        while time.time() - start_time < self.check_status_timeout:
            active_client_list = self.zd.get_active_client_list()
            for client in active_client_list:
                if client['mac'].upper() == sta_wifi_mac_addr.upper():
                    if client['status'] != 'Authorized':
                        # This loop gives the ZD time to update its knowledge of the clients
                        if status_verifying_count == 0:
                            return ("FAIL",
                                    "The station status shown on ZD is '%s' instead of 'Authorized'" % 
                                    client['status'])
                        status_verifying_count = status_verifying_count - 1
                        break
                    if client['ip'] != sta_wifi_ip_addr:
                        if status_verifying_count == 0:
                            return ("FAIL", "The station wifi IP address shown on ZD is %s instead of %s" % 
                                    (client['ip'], sta_wifi_ip_addr))
                        status_verifying_count = status_verifying_count - 1
                        break
                    client_info_on_zd = client
                    break
            if client_info_on_zd:
                logging.info("The active client information: ip address ----- %s; status ----- %s" % 
                             (client_info_on_zd['ip'], client_info_on_zd['status']))
                break
            time.sleep(1)

        if not client_info_on_zd:
            logging.debug("Active Client List: %s" % str(active_client_list))
            return ("FAIL", "Zone Director didn't show any info about the target station (with MAC %s)" % sta_wifi_mac_addr)

#        logging.info("Ping to %s from the target station (timeout: %s)" % (self.ip_addr, self.ping_timeout))
#        ping_result = self.target_station.ping(self.ip_addr, self.ping_timeout * 1000)
#        if ping_result.find("Timeout") != -1:
#            logging.info("Ping FAILED")
#            return ("FAIL", "The target station could not send traffic while it has full access to the wireless network")
#        else:
#            logging.info("Ping OK ~~ %s second(s)" % ping_result)

        return ["", ""]

    def _verify_disassociated_client(self):
        """
        Verify information of target station when it can not associate to the wlan
        """
        logging.info("The station is in the denied list of ACL, make sure the station can not associate to the WLAN")
        start_time = time.time()
        while time.time() - start_time <= self.check_status_timeout:
            if self.target_station.get_current_status() == "connected":
                msg = "The target station can associate to the wireless network "
                msg += "while it is in the denied list of ACL"
                return ["FAIL", msg]
            time.sleep(10)
        if time.time() - start_time > self.check_status_timeout:
            logging.info("The target station disconnects from the ZD now")

        logging.info("Verify information of the target station shown on the Zone Director")
        start_time = time.time()
        while time.time() - start_time < self.check_status_timeout:
            active_client_list = self.zd.get_active_client_list()
            for client in active_client_list:
                if client['mac'].upper() == self.sta_wifi_mac_addr.upper():
                    logging.debug("Client information: %s" % str(client))
                    msg = "The entry of target station appears in the Active Client table "
                    msg += "while it can not associate to the WLAN"
                    return ["FAIL", msg]
#                time.sleep(1)
            time.sleep(50)
        logging.debug("Active client list: %s" % str(active_client_list))
        logging.info("There is no entry of the target station %s on the zoneDirector" % 
                     self.target_station.get_ip_addr())

        return ["", ""]

    def _verify_acl_functionality(self, acl_name):
        """
        Verify funtionality of an ACL when it applied to the wlan. If the station matches with ACL,
        it can associate to the wlan successfully. If the station does not match with ACL, it can not associate
        to the wlan.
        Input:
        - acl_name: name of ACL
        """
        self.wlan_cfg['acl_name'] = acl_name
        logging.info("Configure a WLAN-enabled ACL with SSID %s and ACL %s on the Zone Director" % 
                     (self.wlan_cfg['ssid'], acl_name))
          
        Helpers.zd.wlan.edit_wlan(self.zd, self.wlan_cfg['ssid'], self.wlan_cfg, pause = 5)        
#        self.zd.cfg_wlan(self.wlan_cfg)
#        import pdb
#        pdb.set_trace()
        self.zd.edit_acl_rule(old_acl_name = acl_name, is_modified_policy = True, new_policy = True)
        logging.info("Configure a WLAN with SSID %s on the target station %s" % 
                    (self.wlan_cfg['ssid'], self.target_station.get_ip_addr()))
        self.target_station.cfg_wlan(self.wlan_cfg)

        status, msg = self._verify_associated_client()
        if status == "FAIL":
            return [status, msg]
                
        # Change policy of ACL to 'deny-all' and verify that the target station can not associate to the wlan
        logging.info("Change policy of the ACL to \'deny-all\'")
        self.zd.edit_acl_rule(old_acl_name = acl_name, is_modified_policy = True, new_policy = False)
        self._remove_wlan_on_station()

        logging.info("Configure a WLAN with SSID %s on the target station %s one more time" % 
                    (self.wlan_cfg['ssid'], self.target_station.get_ip_addr()))
        self.target_station.cfg_wlan(self.wlan_cfg)
        status, msg = self._verify_disassociated_client()
        if status == "FAIL":
            return [status, msg]
                
        return ["", ""]

    def _remove_wlan_on_station(self):
        """
        Remove all wlan profiles on the remove station, and verify its status to make sure that it completely
        disconnects from the wireless networks
        """
        logging.info("Remove all WLAN profiles on the remote station")
        self.target_station.remove_all_wlan()

        logging.info("Make sure the target station disconnects from the wireless networks")
        start_time = time.time()
        while True:
            if self.target_station.get_current_status() == "disconnected":
                break
            time.sleep(1)
            if time.time() - start_time > self.check_status_timeout:
                raise Exception("The station did not disconnect from wireless network within %d seconds" % 
                                self.check_status_timeout)
    
    def _retrive_carrier_bag(self):
        l = []
        acl_name = "Test_ACLs_%d"
        for i in range(32):            
            l.append(acl_name % i)
        
        self.carrierbag['existed_acl_name_list'] = l
        self.carrierbag['existed_num_of_acl_entries'] = 32
        self.acl_name_list = self.carrierbag['existed_acl_name_list']
        self.num_of_acl_entries = self.carrierbag['existed_num_of_acl_entries']

    def _update_carrier_bag(self):
        pass                
                