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
        
        
Create on 2012-10-15
@author: kevin.tan@ruckuswireless.com
'''

import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector

from RuckusAutoTest.components.lib.zd import ap_group
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common import lib_Constant as CONST
from RuckusAutoTest.components.lib.zd import node_zd

APGRP_DEFAULT_NAME = 'System Default'

IPMODE_PARENT = '*'
IPMODE_IPV4 = '1'
IPMODE_IPV6 = '2'
IPMODE_DUAL = '3'

nn = {IPMODE_IPV4: 'ipv4',
      IPMODE_IPV6: 'ipv6',
      IPMODE_DUAL: 'dual',
     }

new_apgrp = 'new-apgrp-created'

class CB_ZD_Dualstack_IPmode_APgroup_Negative_Test(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.l3switch = self.testbed.components['L3Switch']

        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.apmac = self.active_ap.base_mac_addr
        self.active_ap_connection_port = self.testbed.mac_to_port[self.apmac]

        self.passmsg = ''
        self.errmsg = ''

    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()

    def test(self):
        #IP mode data base can deploy to AP again correctly and function works fine
        ap_group.delete_all_ap_group(self.zd)
        ap_group.set_ap_group_ip_mode_by_name(self.zd, APGRP_DEFAULT_NAME, IPMODE_DUAL)
        lib.zd.ap.set_ap_network_setting_by_mac(self.zd, self.apmac, IPMODE_PARENT)

        #verify after reboot ZD
        try:
            logging.info("verify IP mode in AP and AP group after reboot ZD")
            self._verify_after_zd_reboot()
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
            
            #verify after reboot active AP
            logging.info("verify IP mode in AP and AP group after reboot active AP")
            self._verify_after_ap_reboot()
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
    
            #verify after AP lost heart beat and re-connect ZD again
            logging.info("verify IP mode in AP and AP group after AP lost heart beat and re-connect ZD again")
            self._verify_ap_heartbeat_lost_and_reconnect()
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
    
            #verify after remove AP and AP rejoin, IP mode data base will lost
            logging.info("verify IP mode in AP and AP group after remove AP and AP rejoin, IP mode data base will lost")
            self._verify_ap_removed_and_reconnect()
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
        except:
            pass
        
        return self.returnResult('PASS', 'IP mode negative test of AP group passed')
    
    def _verify_after_zd_reboot(self):
        self._negative_test_config()

        #restart ZD
        node_zd.restart_zd(self.zd, z_pause4ZDRestart = 5)
        self.zdcli.re_initialize()

        self._verify_config_after_negative_operation()

    def _verify_after_ap_reboot(self):
        self._negative_test_config()

        #restart AP
        self.zd.restart_aps(self.apmac)

        self._verify_config_after_negative_operation()

    def _verify_ap_heartbeat_lost_and_reconnect(self):
        self._negative_test_config()
        self.zd.clear_all_events()

        #Disable switch port of active AP
        logging.info("Close connection to AP [%s %s] before disabling its switch port."
                    % (self.apmac, self.active_ap.ip_addr))
        self.active_ap.close()
        logging.info("Disable the switch port %s connected to the AP [%s %s]" \
                    % (self.active_ap_connection_port,
                       self.apmac, self.active_ap.ip_addr))
        self.l3switch.disable_interface(self.active_ap_connection_port)

        #MSG_AP_lost_heartbeat={ap} heartbeats lost
        expected_event = self.zd.messages['MSG_AP_lost_heartbeat']
        expected_event = expected_event.replace("{ap}", r"AP[%s]" )
        expected_event = expected_event % (self.apmac)

        time0 = time.time()
        wait_time = 360
        time.sleep(15)
        while(True):
            current_time = time.time()
            if  (current_time-time0) >wait_time:
                self.errmsg += 'active AP heart beat lost not occur when disable AP interface in L3 switch, '
                return

            try:
                ap_info= lib.zd.aps.get_ap_brief_by_mac_addr(self.zd, self.apmac)

                if ap_info['state'].lower().startswith('disconnected'):
                    all_events = self.zd.getEvents()
                    event_exist = False
                    for event in all_events:
                        if expected_event in event:
                            event_exist = True
                            break
                    if event_exist == True:
                        break
            except:
                pass

            time.sleep(3)


        logging.info("Enable the switch port %s connected to the AP [%s]" \
                    % (self.active_ap_connection_port,
                       self.apmac))
        self.l3switch.enable_interface(self.active_ap_connection_port)

        time0 = time.time()
        wait_time = 120
        while(True):
            current_time = time.time()
            if  (current_time-time0) >wait_time:
                self.errmsg += 'active AP not connected to ZD when enable AP interface in L3 switch, '
                return

            try:
                ap_info= lib.zd.aps.get_ap_brief_by_mac_addr(self.zd, self.apmac)

                if ap_info['state'].lower().startswith('connected'):
                    all_events = self.zd.getEvents()
                    event_exist = False
                    for event in all_events:
                        if expected_event in event :
                            event_exist = True
                            break
                    if event_exist == True:
                        break
            except:
                pass

            time.sleep(3)
        
        self._verify_config_after_negative_operation()

    def _verify_ap_removed_and_reconnect(self):
        self._negative_test_config()
        self.zd.clear_all_events()

        #remove AP from WebUI
        logging.info("Remove active ap from ZD webUI.")
        self.zd.remove_approval_ap(self.apmac)
        
        #MSG_AP_delete={ap} deleted by administrator
        expected_event = self.zd.messages['MSG_AP_delete']
        expected_event = expected_event.replace("{ap}", r"AP[%s]" )
        expected_event = expected_event % (self.apmac)

        all_events = self.zd.getEvents()
        event_exist = False
        for event in all_events:
            if expected_event in event :
                event_exist = True
                break

        if event_exist == False:
            self.errmsg += 'There is no event shown on ZD when remove active AP, '

        #wait active AP rejoin ZD again
        #MSG_AP_approv_auto=A new {ap} requests to join and is automatically approved
        expected_event = self.zd.messages['MSG_AP_approv_auto']
        expected_event = expected_event.replace("{ap}", r"AP[%s]" )
        expected_event = expected_event % (self.apmac)

        time0 = time.time()
        wait_time = 300
        time.sleep(30)
        while(True):
            current_time = time.time()
            if  (current_time-time0) >wait_time:
                self.errmsg += 'active AP rejoin not occur when enable AP interface in L3 switch, '
                return

            try:
                ap_info= lib.zd.aps.get_ap_brief_by_mac_addr(self.zd, self.apmac)

                if ap_info['state'].lower().startswith('connected'):
                    all_events = self.zd.getEvents()
                    event_exist = False
                    for event in all_events:
                        if expected_event in event :
                            event_exist = True
                            break
                    if event_exist == True:
                        break
            except:
                pass

            time.sleep(3)

        self._verify_config_after_ap_remove_and_rejoin()

    def _negative_test_config(self):
        ap_group.create_ap_group(self.zd, new_apgrp)
        
        #create new AP group and config active AP
        ap_group.set_ap_group_ip_mode_by_name(self.zd, new_apgrp, IPMODE_DUAL)
        ap_group.move_ap_to_member_list(self.zd, new_apgrp, self.apmac)
        lib.zd.ap.set_ap_network_setting_by_mac(self.zd, self.apmac, IPMODE_IPV4)

        time0 = time.time()
        #wait_time = 120
        #@author: li.pingping @bug: ZF-8452 @since: 2014-5-23
        wait_time = 240
        while(True):
            current_time = time.time()
            if  (current_time-time0) >wait_time:
                self.errmsg += 'active AP reset due to IP address change and not connected after %s second, ' % wait_time
                return

            try:
                ap_info= lib.zd.aps.get_ap_brief_by_mac_addr(self.zd, self.apmac)
                if ap_info['state'].lower().startswith('connected'):
                    break
            except:
                pass

            time.sleep(3)

    def _verify_config_after_negative_operation(self):
        #verify IP mode of active AP on ZD webUI
        info = lib.zd.ap.get_ap_general_info_by_mac(self.zd, self.apmac)
        if info['ap_group'] != new_apgrp:
            self.errmsg += 'active AP is in AP group %s, not in new group %s, ' % (info['ap_group'], new_apgrp)

        info = lib.zd.ap.get_ap_network_setting_by_mac(self.zd, self.apmac)
        if info['ip_mode'] != IPMODE_IPV4:
            self.errmsg += 'active AP IP mode of  is %s, not %s, ' % (info['ip_mode'], IPMODE_IPV4)

        #Restore configuration
        ap_group.delete_all_ap_group(self.zd)
        lib.zd.ap.set_ap_network_setting_by_mac(self.zd, self.apmac, IPMODE_PARENT)

    def _verify_config_after_ap_remove_and_rejoin(self):
        #verify IP mode of active AP on ZD webUI
        info = lib.zd.ap.get_ap_general_info_by_mac(self.zd, self.apmac)
        if info['ap_group'] != new_apgrp:
            self.errmsg += 'active AP is in AP group %s, not in new group %s, ' % (info['ap_group'], new_apgrp)

        info = lib.zd.ap.get_ap_network_setting_by_mac(self.zd, self.apmac)
        if info['ip_mode'] != IPMODE_PARENT:
            self.errmsg += 'active AP IP mode of  is %s, not %s, ' % (info['ip_mode'], IPMODE_PARENT)
        if info['ip_version'] != IPMODE_DUAL:
            self.errmsg += 'default AP IP version of active AP is %s, not %s, ' % (info['ip_version'], IPMODE_DUAL)

        #Restore configuration
        logging.info("Delete new created AP group to restore configuration")
        ap_group.delete_all_ap_group(self.zd)
        lib.zd.ap.set_ap_network_setting_by_mac(self.zd, self.apmac, IPMODE_PARENT)
    
    def cleanup(self):
        self._update_carribag()
