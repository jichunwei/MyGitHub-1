# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_SetupWizardConfiguration class tests the values on the setup wizard.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director.

   Required components: 'ZoneDirector'
   
   Test parameters: a dictionay of default value. The default dictionary is below:
   
   {'language':'English', 'dhcp':'False', 'system_name':'ruckus', 'country_code':'United States', 
   'mesh_enabled':'False', 'wireless1_enabled':'True', 'wireless1_name':'Ruckus-Wireless-1', 
   'authentication_open':'True','guest_wlan_enabled':'False', 'guest_wlan_name':'Ruckus-Guest', 
   'admin_name':'admin', 'admin_password':'','create_user_account_is_checked':'False'}
   
   We can change the value of each item whenever the default configuration is changed. 
   
   Result type: PASS/FAIL 
 
   Results: PASS: All the values on the wizard match with the corresponding ones in the dictinary of default values.
            FAIL: At least one value on the wizard is different from the corresponding one in the dictionary.

   Messages: 
       - if the result is PASS, no message is shown. 
       - if the result is FAIL, an error message is shown.

   Test procedure:
       Config:
           1. Get information of all the connected APs.
       Test:       
           1. Navigate to Admin -->Backup. 
              Click the button 'Restore Factory Default System Settings' to reset the ZD to factory configuration. 
           2. Wait for the Zone Director to be up after restarting. Navigate to the ZD's WebUI. 
           3. Follow the wizard and make sure that all the information on the wizard is default. 
              The default information is set by user as below:

             {'language':'English', 'dhcp':'False', 'system_name':'ruckus', 'country_code':'United States', 
              'mesh_enabled':'False', 'wireless1_enabled':'True', 'wireless1_name':'Ruckus-Wireless-1', 
              'authentication_open':'True','guest_wlan_enabled':'False', 'guest_wlan_name':'Ruckus-Guest',
              'admin_name':'admin', 'admin_password':'','create_user_account_is_checked':'False'}
       Cleanup:
           1. Make sure that all APs recover to their original status.
       
   How it was tested:
       1.  Change the a default value the test must return FAIL.

"""

import os
import time
import logging
import pdb

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import te_mgmt_vlan_hlp as TE
from RuckusAutoTest.components import NetgearSwitchRouter as NSR
from RuckusAutoTest.common.sshclient import sshclient

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_SetupWizardConfiguration(Test):
    required_components = ['ZoneDirector', 'L3Switch']
    parameter_description = {}

    def config(self, conf):
        self.list_of_ap_cfg = list()
        self.list_of_connected_aps = list()
        print "Get information of all connected APs"
        self.conf = conf
        if self.conf.has_key('debug'): pdb.set_trace()
        logging.info("Get the list of connected APs")
        if self.conf.has_key('zd'):
            self.zd=self.carrierbag[self.conf['zd']]
            if self.conf['zd']=='lower_mac_zd':
                self.zdcli=self.carrierbag['lower_mac_zdcli']
            elif self.conf['zd']=='higher_mac_zd':
                self.zdcli=self.carrierbag['higher_mac_zdcli']
            elif self.conf['zd']=='zd1':
                self.zdcli=self.carrierbag['zdcli1']
            elif self.conf['zd']=='zd2':
                self.zdcli=self.carrierbag['zdcli2']
        else:
            self.zd = self.testbed.components['ZoneDirector']
            self.zdcli=self.testbed.components['ZoneDirectorCLI']
        self.mgmt_vlan = TE.MVLAN.get_node_mgmt_vlan_info(self.zd) if self.zd.has_mgmt_vlan else {}
        if not self.conf.has_key('zd'):
            l = self.zd.get_all_ap_info()
            for ap in l:
                if ap['status'].lower().startswith(u"connected"):
                    self.list_of_connected_aps.append(ap)
            if not self.list_of_connected_aps:
                raise Exception("No AP connected")
            logging.info("List of connected APs: %s" % self.list_of_connected_aps) 
        
            logging.info("Get all connected APs' configuration")
        for ap in self.list_of_connected_aps:
            self.list_of_ap_cfg.append(self.zd.get_ap_cfg(ap['mac']))
        logging.debug("List of APs' configuration: %s" % self.list_of_ap_cfg)
        
        self.mesh_name = "Mesh-" + self.zd.get_serial_number()
        logging.info("The SSID of Mesh: %s" % self.mesh_name)
        self._store_mgmt_vlan_info()

    def test(self):
        if self.conf.has_key('debug'): pdb.set_trace()
        logging.info("Check the default information of the set up wizard configuration")
        self.conf['mesh_name'] = self.mesh_name
        # self.testbed.components['ZoneDirector'].setup_wizard_cfg(self.conf)
        self.zd.do_login()
        self._reset_factory_and_untag_zd_switch_port()
        self.zd._setup_wizard_cfg(self.conf, {}) 
        self._restore_mgmt_vlan_info()
        logging.info("Setup wizard configuration successfully")
        try:
            self.zdcli.do_shell_cmd('')
        except:
            self.zdcli.zdcli = sshclient(self.zdcli.ip_addr, self.zdcli.port,'admin','admin')
            self.zdcli.login()
        logging.info("zdcli log in succ")
        
        self.zd.navigate_to(self.zd.CONFIGURE, self.zd.CONFIGURE_SYSTEM)
        self.zd.s.click_if_not_checked("//input[@id='high']")
        self.zd.s.click("//input[@id='apply-log']")
        
        if self.mgmt_vlan:
            return ("PASS", str(self.mgmt_vlan))
        else:
            return "PASS", "reset factory [%s] and Setup wizard configuration successfully" % self.zd.ip_addr

    def cleanup(self):
        if not self.conf.has_key('zd'):
            time.sleep(90)
            print "Clean up: Wait for APs to reconnect"
            logging.info("Waiting for APs to reconnect. This process takes some minutes. Please wait... ")
            ap_upgrade_timeout = 150
            ap_upgrade_start_time = time.time()
            for associated_ap in self.list_of_connected_aps:
                while(True):
                    if (time.time() - ap_upgrade_start_time) > ap_upgrade_timeout:
                        raise Exception("Error: AP upgrading failed. Timeout")
                    current_ap = self.zd.get_all_ap_info(associated_ap['mac'])
                    if current_ap:
                        if current_ap['status'] == associated_ap['status']:
                            break
     
            logging.info("Set APs to their original configuration.")
            for ap_cfg in self.list_of_ap_cfg:
                self.zd.set_ap_cfg(ap_cfg)

###
###
###
    def _store_mgmt_vlan_info(self):
        if self.mgmt_vlan:
            logging.info("MgmtVlan installed; gather its information") 
            # if L3Switch not presented; let the test fail anyway
            self.l3sw = self.testbed.components['L3Switch']
            # Can python's class initialized from its parent instance?
            nsr_conf = dict(ip_addr = self.l3sw.ip_addr, username = self.l3sw.username,
                            password = self.l3sw.password, enable_password = self.l3sw.enable_password)
            self.nsr = NSR.NetgearSwitchRouter(nsr_conf)
            self.mgmt_vlan['swp'] = TE.get_zd_switch_port(self.zd, self.nsr) 
            logging.info("MgmtVlan attrs: %s" % str(self.mgmt_vlan))
        
    def _reset_factory_and_untag_zd_switch_port(self):
        self.wait_for_alive = False if self.mgmt_vlan and self.mgmt_vlan['zd']['enabled'] else True
        # ZoneDirector._reset_factory() changed to not wait for ZD come alive
        # if ZD MgmtVlan is enabled.
        self.zd._reset_factory(self.wait_for_alive)
        if not self.wait_for_alive:
            # ZD port is tagged; after reset_factory; the port need to be untagged
            TE.NSRHLP.untag_switch_vlan_interface(self.nsr,
                                               self.mgmt_vlan['swp']['vlan_id'],
                                               self.mgmt_vlan['swp']['interface'],)
            # ATTN: step to reset_factoryWaitForAlive() immeidately
            try:
                # ZD is being reset and restarted
                self.zd._reset_factory_wait_for_alive_s1()
            except:
                # ZD is restarted
                self.zd._reset_factory_wait_for_alive_s2()

    def _restore_mgmt_vlan_info(self):
        if self.mgmt_vlan:
            if self.mgmt_vlan['zd']['enabled']:
                self.mgmt_vlan2 = TE.tag_zd_mgmt_vlan(self.zd,
                                                  self.nsr,
                                                  self.mgmt_vlan['swp']['interface'],
                                                  self.mgmt_vlan['swp']['vlan_id'],)
                time.sleep(2)
            ap_mgmt_vlan = self.mgmt_vlan['ap']['mgmt_vlan']
            if ap_mgmt_vlan['enabled'] and ap_mgmt_vlan['vlan_id']:
                if self.mgmt_vlan['ap']['zd_discovery']['enabled']:
                    prim_ip = self.mgmt_vlan['ap']['zd_discovery']['prim_ip']
                    sec_ip = self.mgmt_vlan['ap']['zd_discovery']['sec_ip']
                else:
                    prim_ip = sec_ip = u''
                self.appolicy2 = TE.tag_ap_mgmt_vlan(self.zd,
                                                  ap_mgmt_vlan['vlan_id'],
                                                  prim_ip, sec_ip)

