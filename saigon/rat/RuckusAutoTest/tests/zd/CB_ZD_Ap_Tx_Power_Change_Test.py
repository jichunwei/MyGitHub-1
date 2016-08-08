# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
 
"""

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.components.lib.zd import access_points_zd as AP
from RuckusAutoTest.components.lib.apcli import shellmode as ap_shell

class CB_ZD_Ap_Tx_Power_Change_Test(Test):
    def config(self, conf):
        self.conf={'ap_mac_list':[],
                   'list_of_radio_list':[],
                    'check_status_timeout': 60,
                    'break_time': 10,
                    'restart_cnt': 6,}
        self.conf.update(conf)
        if len(self.conf['ap_mac_list'])!=len(self.conf['list_of_radio_list']):
            raise('the length of ap list(%s) and radio list(%s) is not the same'%(self.conf['ap_mac_list'],self.conf['list_of_radio_list']))
        self.zd=self.testbed.components['ZoneDirector']
        #get ap info
        self.ap_list=[]
        self.ap_mac_list=self.conf['ap_mac_list']
        self.list_of_radio_list=self.conf['list_of_radio_list']
        for idx in range(0,len(self.ap_mac_list)):
            ap_info=self.zd.get_all_ap_info(self.ap_mac_list[idx])
            ap_info.update({'supported_radio_list':self.list_of_radio_list[idx]})
            self.ap_list.append(ap_info)
        logging.info('there are %d ap to test,they are %s'%(len(self.ap_list),self.ap_list))
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        self.errmsg=''
        self.passmsg=''
    def test(self):
        for ap in self.ap_list:
            self._ap_tx_power_change_test(ap)
        if self.errmsg:
            return('FAIL',self.errmsg)
        return('PASS','ap txpower change in zd web UI works correctly')

    def cleanup(self):
        pass
    
    def _get_ap_full_power(self,ap_info,ap,radio):
        AP.set_ap_tx_power(self.zd,ap_info['mac'],radio)
        time.sleep(3)
        return ap.sh_get_radio_tx_power(radio)
    
    def _ap_tx_power_change_test(self,ap_info):
        radio_list=ap_info['supported_radio_list']
        power_change_list=[1,2,3,4,5,6,7,8,9,10,'Auto','Min','Global']
        ap = RuckusAP(dict(ip_addr = ap_info['ip_addr'],username='admin',password='admin'))
        for radio in radio_list:
            logging.info('begin ap %s(%s) radio %s test'%(ap_info['mac'],ap_info['model'],radio))
            full_power=self._get_ap_full_power(ap_info,ap,radio)
            logging.info('ap full tx power in radio %s is %s'%(radio,full_power))
            msg_prefix='ap %s,model %s,radio:%s,full power'%(ap_info['mac'],ap_info['model'],radio)
            if radio=='2.4':
                radio_mode='ng'
            else:
                radio_mode='na'
                
            #assign wlan group to ap radio
            errmsg=self._apply_wlangroup_to_active_ap(ap_info['mac'],radio_mode)
            if errmsg:
                self.errmsg='%s apply wlan group to ap %s radio mode %s failed:%s'%(msg_prefix,ap_info['mac'],radio_mode,errmsg)
                logging.info(self.errmsg)
                lib.zd.ap.assign_to_default_wlan_group(self.zd,ap_info['mac'])  
                break
            logging.info('%s apply wlan group to ap %s radio mode %s successfully'%(msg_prefix,ap_info['mac'],radio_mode))
            
            #associate sta to wlan
            errmsg=self._test_assoc_station_with_ssid(self.conf['wlan_cfg'])
            if errmsg:
                self.errmsg='%s associate sta to wlan %s failed:%s'%(msg_prefix,self.conf['wlan_cfg']['ssid'],errmsg)
                logging.info(self.errmsg)
                lib.zd.ap.assign_to_default_wlan_group(self.zd,ap_info['mac'])  
                break
            logging.info('%s associate sta to wlan %s successfully'%(msg_prefix,self.conf['wlan_cfg']['ssid']))
            #ping dest ipaddr
            errmsg=self._testClientPingDestIsAllowed()
            if errmsg:
                self.errmsg='%s sta ping destination addr failed:%s'%(msg_prefix,errmsg)
                logging.info(self.errmsg)
                lib.zd.ap.assign_to_default_wlan_group(self.zd,ap_info['mac'])  
                break
            logging.info('%s sta ping destination addr successfully'%(msg_prefix))
            
            for power_change in power_change_list:
                logging.info('set ap %s,radio %s,txpower change to %s'%(ap_info['mac'],radio,power_change))
                AP.set_ap_tx_power(self.zd,ap_info['mac'],radio,power_change)
                msg_prefix='ap %s,model %s,radio:%s,power change:%s'%(ap_info['mac'],ap_info['model'],radio,power_change)
                
                #ping dest ip address
                errmsg=self._testClientPingDestIsAllowed()
                if errmsg:
                    self.errmsg='%s sta ping destination addr failed:%s'%(msg_prefix,errmsg)
                    logging.info(self.errmsg)
                    break
                logging.info('%s sta ping destination addr successfully'%(msg_prefix))
                
                if power_change=='Auto' or power_change=='Global':
                    expected_power=full_power
                elif power_change=='Min': 
                    expected_power=1
                else:
                    expected_power=full_power-power_change
                logging.info('the ap tx_power should be %s'%expected_power)
                time.sleep(10)
                tx_power=ap_shell.get_radio_tx_power(ap,radio)
                logging.info('the ap tx_power is %s'%tx_power)
                if tx_power!=expected_power:
                    self.errmsg+='ap %s txpower not correct,radio %s,full power %s,power change %s,tx power is %s;'%\
                    (ap_info['mac'],radio,full_power,power_change,tx_power)
                    break
                time.sleep(10)
                
            #after one radio test,assign ap to default wlan group
            logging.info('radio %s test is finished,assign ap %s to default wlan group'%(radio,ap_info['mac']))
            lib.zd.ap.assign_to_default_wlan_group(self.zd,ap_info['mac'])  
            if self.errmsg:
                break
                

    def _apply_wlangroup_to_active_ap(self,ap_mac,radio_mode):
        logging.info('apply wlangroup %s to ap %s'%(self.conf['wlan_group_name'],ap_mac))
        errmsg=None
        try:
            lib.zd.ap.assign_to_wlan_group(self.zd,ap_mac,radio_mode, self.conf['wlan_group_name'])
            passmsg = 'The WLAN group "%s" is apply to the ap %s successfully'
            passmsg = passmsg % (self.conf['wlan_group_name'],ap_mac)
            logging.info(passmsg)
        except Exception, e:
            errmsg = '[Apply failed]: %s' % e.message
        
        return errmsg
            
    def _test_assoc_station_with_ssid(self,wlan_cfg):

        errmsg = tmethod.assoc_station_with_ssid(
            self.target_station, wlan_cfg,self.conf['check_status_timeout'],
            self.conf['break_time'], self.conf['restart_cnt'],
        )
        
        return errmsg 
    
    def _testClientPingDestIsAllowed(self):
        errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, 
                                                          self.conf['dest_ip'], 
                                                          ping_timeout_ms = self.conf['ping_timeout_ms'])
        return errmsg
        
