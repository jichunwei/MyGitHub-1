#encoding:utf-8
'''
Created on 2013-05-15

@author: ye.songnan@odc-ruckuswireless.com

Description:

1.Randomly get two real ap's MAC from testbed.
2.Get the two ap's IP address via MAC.
3.SSH to AP by IP address .
4.Get wlan-list by CLI.
5.Get SSID of wlan in wlan-list.
6.Verify wlan deploy successfully.

'''

import logging
import random
import re
import copy
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_ap
from RuckusAutoTest.components.lib.apcli.shellmode import get_radio_band
from RuckusAutoTest.components import create_ruckus_ap_by_ip_addr

class CB_AP_CLI_Random_AP_Check_Wlan(Test):
    
    def config(self,conf):
        self._cfg_init_test_params(conf)
    
    def test(self):
        #Randomly get two real ap's MAC from testbed.
        random_ap_mac_list = self._get_random_ap(self.conf['apnums'])
        
        #Get the two real ap's IP address via MAC.
        random_ap_ip_list = []
        for mac in random_ap_mac_list:
            random_ap_ip_list.append(configure_ap._get_ap_info_by_mac(self.zdcli, mac)['Network Setting']['IP Address'])

#------------------------------------------------------------------------------------------------------------------------                     
        t0=time.time() 
        ap_deploy_tag_list = []   
        ap_cli_list = []
        for i in range(len(random_ap_ip_list)):
            ap_deploy_tag_list.append(False)
            ap_ip = random_ap_ip_list[i]
            ap_cli = create_ruckus_ap_by_ip_addr(ip_addr=ap_ip, username ='admin', password='admin', timeout=30)
            ap_cli_list.append(ap_cli)
        
        #check two real ap's deplopyment within 30mins    
        while True:
            if time.time()-t0>self.timeout:
                self.errmsg='check ap wlan deploy time out'
                break
            
            for i in range(len(random_ap_ip_list)):
                ap_cli = ap_cli_list[i]
                d_ap_wlanlist = ap_cli.get_wlan_info_dict()
                #Get radio band
                ap_radio = get_radio_band(ap_cli)  
                
                if not ap_deploy_tag_list[i]:
                    #Get SSID of wlan in wlan-list
                    ap_up_wlan_0_31, ap_up_wlan_32_63 = self.ap_get_ssid_sorted_list(d_ap_wlanlist, ap_cli)
                    #Verify wlan deploy successfully
                    ap_ip = random_ap_ip_list[i]
                    result = self.ap_verify_wlan_deploy(ap_ip, ap_radio, ap_up_wlan_0_31, ap_up_wlan_32_63)
                    if result == 'OK':
                        ap_deploy_tag_list[i] = True
                        
            if False not in ap_deploy_tag_list:
                logging.info('deploy success')
                break
#------------------------------------------------------------------------------------------------------------------------------------------            
            
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self.passmsg = '[ZDCLI] Verify wlan deploy successfully.' 
            return self.returnResult('PASS', self.passmsg)
#-----------------------------------------------------------------------------------------------------------------------                
    
    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        
        self.conf = {'wlan_list':[], 
                        'apnums':2,
                        'timeout':120,
                        }        
        self.conf.update(conf)
        self.timeout = self.conf['timeout']*15 #120*15 = 1800s =30mins

        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.wlan_name_list = self.carrierbag['wlan_name_list']  
       
    #Get random two real ap's mac
    def _get_random_ap(self, apnums):
        ap_sym_dict = copy.deepcopy(self.testbed.get_aps_sym_dict())
        real_ap_mac_list = []
        for apinfo in ap_sym_dict.values():
            if apinfo['model'].startswith('zf7363') :
                real_ap_mac_list.append(apinfo['mac'])

        random_ap_list = []        
        for i in range(apnums):
            random_ap = random.choice(real_ap_mac_list)
            real_ap_mac_list.remove(random_ap)
            random_ap_list.append(random_ap)
        return random_ap_list
        
    #Get SSID of wlan in wlan-list
    def ap_get_ssid_sorted_list(self,d_ap_wlanlist, ap_cli):
        ap_up_wlan_0_31 = []
        ap_up_wlan_32_63 = []
        
        for wlan_attr in d_ap_wlanlist.values():      
            if wlan_attr['name'].startswith('wlan') and wlan_attr['type'] == 'AP' and wlan_attr['status'] == 'up':
                wlan_name = ap_cli.get_ssid(wlan_attr['name'])
                num = int((re.match(r'wlan(\d+)',wlan_attr['name'])).group(1))
                if num in range(32):
                    ap_up_wlan_0_31.append(wlan_name)
                if num in range(32, 64):
                    ap_up_wlan_32_63.append(wlan_name)    
    
        ap_up_wlan_0_31.sort() 
        ap_up_wlan_32_63.sort() 
        
        return (ap_up_wlan_0_31, ap_up_wlan_32_63)
    
    #Verify wlan deploy successfully  
    def ap_verify_wlan_deploy(self, ap_ip, ap_radio, ap_up_wlan_0_31, ap_up_wlan_32_63):
        if ap_radio == 2:
            if self.wlan_name_list == ap_up_wlan_0_31 and self.wlan_name_list == ap_up_wlan_32_63:
                msg = 'Wlans deploy on AP-%s OK.' %ap_ip
                logging.info(msg)
                result = 'OK'
                return result
            else:
                self.msg='Wlans deploy on AP-%s Failed.' %ap_ip
                logging.info(self.msg)
                result = 'FAILED'
                return result
        elif ap_radio == 1:
            if self.wlan_name_list == ap_up_wlan_0_31:
                msg = 'Wlans deploy on AP-%s OK.-2.4G' %ap_ip
                logging.info(msg)
                result = 'OK'
                return result
            else:
                self.msg='Wlans deploy on AP-%s Failed.-2.4G' %ap_ip
                logging.info(self.msg)
                result = 'FAILED'
                return result
        else:
                self.msg='The model is neither single band or dual band.'  
                logging.info(self.msg) 
                result = 'FAILED'
                return result

            
