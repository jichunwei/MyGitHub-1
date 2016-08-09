# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
"""
Description: This script is support to test spectralink phone with different encryption
Author: Jason Lin
Email: jlin@ruckuswireless.com

Test Parameters: {'radio': define radio config of dut phone, 'a', 
                  'ssid': define ssid of dut phone, '8030WPA2-11a', 
                  'mac_addr': define mac address of dut phone, '00:90:7a:06:e9:bc'}
Result type:PASS/FAIL
Results:PASS:the dut phone could get an ip address and reply ping to TE.
        FAIL:the dut phone could not obtain an ip address or reply ping to TE.
                  
Test Procedure:
1. config:
   - delete dhcp records in leases file of dhcp server
2. test:
   - verify ssid of dut phone include data, video wlan exist on ZD 
   - assign ssid of dut to wlan group
   - verify wlans are delopyed to active AP
   - capture a ip address on leases file of dhcp server
   - send a ping to dut phone
   - verify dut phone infomation shown on ZD 
   - verify dut phone infomation shown on AP
3. cleanup:
   - remove wlans include data, video wlan from wlan group
"""
import time
import logging
import libZD_TestMethods as tmethod
import libZD_TestMethods_v8 as tmethod8

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helper_ZD as zhlp
from RuckusAutoTest.common import Ratutils as utils
from pprint import pformat
from RuckusAutoTest.scripts.zd import spectralink_phone_config as splk_cfg

class CB_ZD_Test_SPLK_Phone_Encrypt(Test):
    
    def config(self, conf):
        self._cfgInitTestParams(conf)
        self.dhcpserver.delete_dhcp_leases()

    def test(self):
        self._verifyPhoneSsidExistOnZD()
        if self.errmsg: return self.returnResult("FAIL", self.errmsg)
        self._testWlanIsUp()
        if self.errmsg: return self.returnResult("FAIL", self.errmsg)
        #self._turn_on_phone()
        #self._getIpfromDhcpServer()
        #if self.errmsg: return self.returnResult("FAIL", self.errmsg)
        self._testTEPingPhone()
        if self.errmsg: return self.returnResult("FAIL", self.errmsg)
        self._testVerifyStationInfoOnZD()
        if self.errmsg: return self.returnResult("FAIL", self.errmsg)
        self._testVerifyStationInfoOnAP()
        if self.errmsg: return self.returnResult("FAIL", self.errmsg)
        self.carrierbag['active_phone'] = self.phone_cfg
        msg = "The Phone associated wlan [%s] successfully and respone time is %s sec" %\
              (self.phone_cfg['ssid'], self.phone_response_time)
              
        return self.returnResult("PASS", msg)
        
    def cleanup(self):
        pass
        #self._removeActiveWlansFromWlanGroup()
        #self.carrierbag['active_phone']={}
        
    def _cfgInitTestParams(self, conf):
        self.conf = dict( ping_timeout=90,
                          check_status_timeout=240,
                          check_wlan_timeout=30,
                          check_dhcp_timeout=60,
                          break_time=3,
                          radio_mode='')
        self.conf.update(conf)
        self.errmsg = ''
        self.phone_cfg = conf.copy()
        self.zd = self.testbed.components['ZoneDirector']
        self.dhcpserver = self.testbed.components['LinuxServer']
        self.push_dev = self.testbed.components['PushKeypadDevice']
        self.wgs_cfg = self.carrierbag['wgs_cfg'].copy()
        self.phone=self.phone_cfg['ssid']
        self.wlan_cfg = self.carrierbag[self.phone].copy()
        self.active_wlan_list=[]
        self.active_wlan_list.append(self.wlan_cfg['ssid'])
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.pwr_key =splk_cfg.get_ph_cfg(self.phone)['pwr_key']
    
    def _verifyPhoneSsidExistOnZD(self):
        if not self.carrierbag.has_key(self.phone_cfg['ssid']):
            self.errmsg = "ZD doesn't have wlan[%s] created already" % self.phone_cfg['ssid']
        
    def _assignPhoneSsidToWGS(self):
        self.errmsg = zhlp.wgs.cfg_wlan_group_members(self.zd, self.wgs_cfg['name'], self.active_wlan_list, True)
        tmethod8.pause_test_for(15, 'Wait for ZD to push config to the APs')

    def _testWlanIsUp(self):
        for wlan_name in self.active_wlan_list:
            self.errmsg = tmethod8.check_wlan_on_ap_is_up( self.active_ap,
                                                           wlan_name,
                                                           self.conf['check_wlan_timeout'])
        if self.errmsg:return
        
    def _turn_on_phone(self):
        self.push_dev.turn_on_phone(self.pwr_key)
        tmethod8.pause_test_for(10, 'Wait for Phone[%s] booting' % self.phone)
        
    def _getIpfromDhcpServer(self):
        logging.info("Verify the ip address of phone shown on leases file of dhcp server")
        t = time.time()
        while time.time() - t < self.conf['check_dhcp_timeout']:
            time.sleep(3)
            self.phone_ip = self.dhcpserver.get_ip_addr_in_dhcp_leases_by_mac_addr(self.phone_cfg['mac_addr'])
            logging.debug("Capture the ip address of phone is %s" % self.phone_ip)
            if self.phone_ip: 
                return
        self.errmsg = "Can't get the ip address of PHONE [%s] on leases file of dhcp server" % self.phone_cfg['ssid']

    def _testTEPingPhone(self):
        logging.info("Verify test engine can ping phone")
        self.phone_ip = splk_cfg.get_ph_cfg(self.phone)['ip_addr']        
        ping_result = utils.ping_with_tos( self.phone_ip, timeout_ms=self.conf['ping_timeout']*1000, echo_timeout=1000, tos=224)
        if ping_result.find("Timeout") != -1:
            logging.debug("PHONE [%s] did not response TE over %d sec" % (self.phone_cfg['ssid'], self.conf['ping_timeout']))
            self.errmsg = "PHONE [%s] did not response TE over %d sec" % (self.phone_cfg['ssid'], self.conf['ping_timeout'])
        else:
            logging.info("PHONE [%s] response time is %s" % (self.phone_cfg['ssid'], ping_result))
            self.phone_response_time = ping_result
        
    def _testVerifyStationInfoOnZD(self):
        tmethod8.pause_test_for(60, 'Wait for ZD update active client infomation')
        logging.info("Verify information of the phone shown on the ZoneDirector")
        # Define the expected radio mode
        if self.phone_cfg['radio'] in ['g','b','b/g','bg']:
            expected_radio_mode = r'802.11b/g'
        elif self.phone_cfg['radio'] == 'a':
            expected_radio_mode = r'802.11a'
        else:
            expected_radio_mode = None       
        expected_ip = self.phone_ip
        exp_client_info = {"ip": ( expected_ip, '0.0.0.0'), "status": "Authorized", "wlan": self.phone_cfg['ssid'],
                           "radio": expected_radio_mode, "apmac": self.active_ap.get_base_mac()}
        self.errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.zd,
                                                                   self.phone_cfg['mac_addr'], exp_client_info,
                                                                   self.conf['check_status_timeout'])
        logging.debug("Client infomation shown on ZD \n%s", pformat(self.client_info_on_zd,4,120)) 

        
    def _testVerifyStationInfoOnAP(self):
        self.errmsg = tmethod.verify_station_info_on_ap(self.active_ap, 
                                                    self.phone_cfg['mac_addr'], 
                                                    self.phone_cfg['ssid'],
                                                    self.client_info_on_zd['channel'])
    
    def _removeActiveWlansFromWlanGroup(self):
        logging.info("Remove wlans on wlan group")
        zhlp.wgs.cfg_wlan_group_members(self.zd, self.wgs_cfg['name'], self.active_wlan_list, False)
        tmethod8.pause_test_for(10, 'Wait for ZD to push config to the APs')
