# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_SetupWizardConfiguration class tests the values on the setup wizard.
set zd factory default

"""

import os
import time
import logging
import pdb

from RuckusAutoTest.common.Ratutils import ping
from RuckusAutoTest.models import Test
from RuckusAutoTest.common.sshclient import sshclient
from RuckusAutoTest.components.lib.zd import configure_ip 
#@author:Chico, 2014-8-19, ZF-9706
#from RuckusAutoTest.components.lib.zdcli import show_config
#@author:Chico, 2014-8-19, ZF-9706
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.components.lib.zd import system_zd as sys
from RuckusAutoTest.components.lib.zd import access_points_zd as lib
from RuckusAutoTest.components.lib.zd import aps

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_ZD_Set_Factory_Default(Test):

    def config(self, conf):
        self.list_of_ap_cfg = list()
        self.list_of_connected_aps = list()
        print "Get information of all connected APs"
        self.conf = {'relogin_zdcli':True}
        self.conf.update(conf)
        if self.conf.has_key('debug'): pdb.set_trace()
        logging.info("Get the list of connected APs")
        if self.conf.has_key('zd'):
            self.zd=self.carrierbag[self.conf['zd']]
            if self.conf['zd']=='lower_mac_zd':
                self.zdcli=self.carrierbag['lower_mac_zdcli']
            elif self.conf['zd']=='higher_mac_zd':
                self.zdcli=self.carrierbag['higher_mac_zdcli']
            elif self.conf['zd']=='zd1':
                self.zd = self.carrierbag['zd1']
                if self.carrierbag.get('zdcli1'):
                    self.zdcli=self.carrierbag['zdcli1']
                if self.carrierbag.get('ZDCLI1'):
                    self.zdcli=self.carrierbag['ZDCLI1']
            elif self.conf['zd']=='zd2':
                self.zd = self.carrierbag['zd2']
                if self.carrierbag.get('zdcli2'):
                    self.zdcli=self.carrierbag['zdcli2']
                if self.carrierbag.get('ZDCLI2'):
                    self.zdcli=self.carrierbag['ZDCLI2']
            elif self.conf['zd']=='active_zd':
                self.zdcli=self.carrierbag['active_zd_cli']
            elif self.conf['zd']=='standby_zd':
                self.zdcli=self.carrierbag['standby_zd_cli']
        else:
            self.zd = self.testbed.components['ZoneDirector']
            self.zdcli=self.testbed.components['ZoneDirectorCLI']
        if not self.conf.has_key('zd'):
            self.ap_mac_list=self.testbed.ap_mac_list
            self.list_of_connected_aps=self._get_active_ap_list(self.zd)
            logging.info("List of connected APs: %s" % self.list_of_connected_aps) 
        
        self.mgmt_vlan_enable = False
        if '128' in self.zd.ip_addr:
            self.mgmt_vlan_enable = True
            
        if self.mgmt_vlan_enable:
            if self.zd.ip_addr.endswith('3'):
                self.zd_physical_ip = '192.168.0.3'
            elif self.zd.ip_addr.endswith('2'):
                self.zd_physical_ip = '192.168.0.2'
        
            self.zd_ip_addr = self.zd.ip_addr
        
        self.ap_vlan = '1'
        

    def test(self):
        if self.conf.has_key('debug'): pdb.set_trace()
        logging.info("set zd factory and setup wizard")
        # self.testbed.components['ZoneDirector'].setup_wizard_cfg(self.conf)
        self.zd.do_login()
        ip_before = self.zd.ip_addr
        if self.mgmt_vlan_enable:
            self.zd.ip_addr = self.zd_physical_ip
            self.zd.url = self.zd.conf['url'] = "https://" + self.zd.ip_addr
            ap_vlan = lib.get_ap_mgmt_vlan_in_ap_policy(self.zd)
#@author:Chico, 2014-8-19, ZF-9706
        #ip_info = show_config.get_ip_info(self.zdcli)
        ip_info = sys.get_device_ip_settings(self.zd, const.IPV6)
        # Parameters 'ipv6' will get both ipv4 and ipv6 configuration.
#@author:Chico, 2014-8-19, ZF-9706

        
        self.zd._reset_factory(wait_for_alive = False)
        self._wait_zd_restart_after_set_ip(self.zd,ip_before)
        self.zd._setup_wizard_cfg_totally_followig_defalut_cfg()
        logging.info("Setup wizard configuration successfully")
        time.sleep(60)
        self.zd.login()
        ip_before = self.zd.ip_addr
        
        if self.mgmt_vlan_enable:
            ipconfig = {'type':'manual',
                        'ip_addr':self.zd_ip_addr,
                        'net_mask':'255.255.255.0',
                        'gateway':'192.168.128.253',
                        'pri_dns':'192.168.0.252',
                        'sec_dns':'',
                        'access_vlan':'328'
                        }
            configure_ip.set_zd_ip_setting(self.zd, ipconfig)
            self.zd.ip_addr = self.zd_ip_addr
            self.zd.url = self.zd.conf['url'] = "https://" + self.zd.ip_addr 
            self._wait_zd_restart_after_set_ip(self.zd,ip_before)   
            
        #@author: anzuo, @since: 140110, @change: config ZD ipv6
        try:
            self.zd.s.open(self.zd.url)
        except:
            time.sleep(60)
            self.zd.s.open(self.zd.url)
#@author:Chico, 2014-8-19, ZF-9706
        if ip_info.get('ip_version') in [const.DUAL_STACK, const.IPV6]:
#            default_ip_cfg = {'ip_version': ip_info['ip_version'],
#                              const.IPV4: {'ip_alloc': ip_info.get('ip_addr_mode').lower(),
#                                           'ip_addr': ip_info.get('ip_addr'),
#                                           'netmask': ip_info.get('ip_addr_mask'),
#                                           'gateway': ip_info.get('ip_gateway'),
#                                           'pri_dns': ip_info.get('ip_pri_dns'),
#                                           'sec_dns': ip_info.get('ip_sec_dns'),},
#                              const.IPV6: {'ipv6_alloc': ip_info.get('ipv6_addr_mode').lower(),
#                                           'ipv6_addr': ip_info.get('ipv6_addr'),
#                                           'ipv6_prefix_len': ip_info.get('ipv6_prefix_len'),
#                                           'ipv6_gateway': ip_info.get('ipv6_gateway'),
#                                           'ipv6_pri_dns': ip_info.get('ipv6_pri_dns'),
#                                           'ipv6_sec_dns': ip_info.get('ipv6_sec_dns')},
#                              'vlan': '',
#                              }
            sys.set_device_ip_settings(self.zd, ip_info, const.IPV6)
#@author:Chico, 2014-8-19, ZF-9706
        
        try:
            self.zd.s.open(self.zd.url)
        except:
            time.sleep(60)
            self.zd.s.open(self.zd.url)
            
        self.zd.login()
        
        if self.conf.has_key('renew_entitlement') and self.conf['renew_entitlement']:
            logging.info("upload entitlement file")
            self.zd.renew_entitlement(const.entitlement_path)
        
        if self.ap_vlan != '1':
            lib.set_ap_mgmt_vlan_in_ap_policy(self.zd, self.ap_vlan)

        if self.conf['relogin_zdcli']:
            try:
                self.zdcli.do_shell_cmd('')
            except:
                self.zdcli.zdcli = sshclient(self.zdcli.ip_addr, self.zdcli.port,'admin','admin')
                self.zdcli.login()
                logging.info("zdcli log in succ")
        return "PASS", "reset factory [%s] and Setup wizard configuration successfully" % self.zd.ip_addr

    def cleanup(self):
        if not self.conf.has_key('zd'):
#            time.sleep(90)
            print "Clean up: Wait for APs to reconnect"
            logging.info("Waiting for APs to reconnect. This process takes some minutes. Please wait... ")
            ap_setfactory_timeout = 300
            ap_factory_start_time = time.time()
            for associated_ap in self.list_of_connected_aps:
                while(True):
                    if (time.time() - ap_factory_start_time) > ap_setfactory_timeout:
                        raise Exception("Error: AP set factory failed. Timeout")
 #@author:Chico, 2014-8-20, zd.get_all_ap_info function is out of fashion
                    #current_ap = self.zd.get_all_ap_info(associated_ap['mac'])
                    current_ap = aps.get_ap_brief_by_mac_addr(self.zd, associated_ap['mac'])
                    if current_ap:
                        #if current_ap['status'].lower().startswith('connected'):
                        if current_ap['state'].lower() == 'connected':
#@author:Chico, 2014-8-20, zd.get_all_ap_info function is out of fashion
                            break
                    else: time.sleep(5)

    def _get_active_ap_list(self,zd):
        zd_active_ap_list = []
        logging.info("Get ZD %s all active APs", zd.ip_addr)
        for mac in self.ap_mac_list:
            ap = zd.get_all_ap_info(mac)
            if ap['status'].lower().startswith('connected'):
                zd_active_ap_list.append(ap)
        
        return zd_active_ap_list    
    
    
    def _wait_zd_restart(self,zd):
        logging.info('waitting zd restart')
        time_out = 1200
        start_time = time.time()
        while True:
            if time.time() - start_time > time_out:
                raise Exception("Error: Timeout")

            res = ping(zd.ip_addr)
            if res.find("Timeout") != -1:
                break

            time.sleep(2)

        logging.info("The Zone Director is being restarted. Please wait...")

        while True:
            if time.time() - start_time > time_out:
                raise Exception("Error: Timeout")

            res = ping(zd.ip_addr)
            if res.find("Timeout") == -1:
                break

            time.sleep(2)
        logging.info("The Zone Director restart successfully.")
    
    
    def _wait_zd_restart_after_set_ip(self,zd,ip_before):
        logging.info('waitting zd restart')
        time_out = 1200
        start_time = time.time()
        while True:
            if time.time() - start_time > time_out:
                raise Exception("Error: Timeout")

            res = ping(ip_before)
            if res.find("Timeout") != -1:
                break

            time.sleep(2)

        logging.info("The Zone Director is being restarted. Please wait...")
#        time_out = 600
        while True:
            if time.time() - start_time > time_out:
                raise Exception("Error: Timeout")

            res = ping(zd.ip_addr)
            if res.find("Timeout") == -1:
                break

            time.sleep(2)
        logging.info("The Zone Director restart successfully.")
        time.sleep(5)
    