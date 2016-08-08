#encoding:utf-8
'''
Created on 2013-05-14

@author: ye.songnan@odc-ruckuswireless.com

Description:

Continuously do the following operation(how many times to do controlled by parameter)
Delete all wlans in wlan group
Verify wlan group member
Add all wlans back 
Verify wlan group member

'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_wlan_groups
from RuckusAutoTest.components.lib.zdcli import get_wlan_group

class CB_ZD_CLI_Add_Remove_Wlan_From_Wlangroup(Test):
    required_components = ['ZoneDirectorCLI']
    parameter_description ={
                            'wlan_list':[], #a list with wlan_cfg 
                             'times':10, #default excute times
                             }
        
    def config(self,conf):
        self._cfg_init_test_params(conf)
    
    def test(self):
        #Delete all wlans in wlan group
        configure_wlan_groups.remove_all_wlan_members_from_wlan_group(self.zdcli, 'Default')
        
        for i in range(self.conf['times']):
            #Add 27 wlans in default wlan group
            configure_wlan_groups._add_wlan_members_to_wlan_group(self.zdcli, 'Default', self.conf['wlan_name_list'])
            wlan_member_1 = get_wlan_group.get_wlan_member_list(self.zdcli, 'Default')
            #Verify add 27 wlan to Default wlangroup success
            wlan_member_1.sort()
            if wlan_member_1 ==self.conf['wlan_name_list']:
                msg = 'Wlan group members are the same.'
                logging.info(msg)
            else:
                self.errmsg='wlan group members are not the same yet.'
                logging.info(self.errmsg)
                break     
            #Delete all wlans in wlan group
            configure_wlan_groups.remove_all_wlan_members_from_wlan_group(self.zdcli, 'Default')
            
        #Add 27 wlans in default wlan group
        configure_wlan_groups._add_wlan_members_to_wlan_group(self.zdcli, 'Default', self.conf['wlan_name_list'])
        wlan_member_2 = get_wlan_group.get_wlan_member_list(self.zdcli, 'Default')   
        #Verify add 27 wlan to Default wlangroup success
        wlan_member_2.sort()
        if wlan_member_2 ==self.conf['wlan_name_list']:
            msg = 'Wlan group members are the same.'
            logging.info(msg)
        else:
            self.errmsg='wlan group members are not the same yet.'
            logging.info(self.errmsg)             

        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self.passmsg = '[ZDCLI] Continuously remove and add wlans from Default wlan group successfully.' 
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        
        self.conf = {'wlan_list':[], 'times':10}        
        self.conf.update(conf)
        
        wlan_name_list = []
        for wlan in self.conf['wlan_list']:
            wlan_name_list.append(wlan['ssid'])
        wlan_name_list .sort()
        self.conf['wlan_name_list'] = wlan_name_list  
        self._updateCarrierBag()

        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        if self.conf.get('zdcli'):
            self.zdcli = self.carrierbag[self.conf['zdcli']]   
            
    def _updateCarrierBag(self):
        self.carrierbag['wlan_name_list'] = self.conf['wlan_name_list']
           
        
        
