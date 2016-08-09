"""
Description: check the disconnect event in zd or not 
User[ras.eap.user] disconnected by admin from WLAN[Radius_Enhancement_DM_Hotspot] at AP[58:93:96:2b:b1:40]

Note: you can provide username in the parameters,which means to use exactly this username.
      If you provide station tag instead, this means to use the station mac address as the username.
      If 'dot1'== True, this means to use the 802.1 format mac address as the username.

Author: chentao@odc-ruckuswireless.com
Since:2013-06-08
"""
#@author: chen.tao 2013-12-19 to adapt more mac-bypass formats
import time
import logging
import libZD_TestConfig as tconfig
from RuckusAutoTest.models import Test

class CB_ZD_Check_Event_Disconnect_Message(Test):
    required_components = ['ZoneDirector']
    parameters_description = {'event': 'the event to check',
                              'is_negative': 'negative test or not',
                              'user': 'the username in the event',
                              'wlan': 'the ssid of the wlan in the event',
                              'ap': 'the mac address of the ap',
                              'sta_tag': 'the station tag',
                              'dot1': 'use the dot1 format mac address',
                              'active_ap_tag':'tag of the active ap,for example AP_01'}    
    def config(self, conf):
        time.sleep(20)
        self._initTestParameters(conf)

    def test(self):
        self.event_msg_list = self._get_expect_msg()
        event_list=self.zd.get_events()
        event_found=False
        for event in event_list:
            target_event = str(event[3])
            target_event = target_event.split(' at ')[0]
            if target_event in self.event_msg_list:
                event_found=True
                break
        if event_found:
            if not self.conf['is_negative']:
                return self.returnResult('PASS', 'Right,the event is found')            
            else:
                return self.returnResult("FAIL", 'Wrong the event is found')
        else:
            if self.conf['is_negative']:        
                return self.returnResult('PASS', 'Right the event is not found')
            else:
                return self.returnResult('FAIL', 'Wrong the event is not found')

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'event':'',
                     'is_negative':False,
                     'user':'',
                     'wlan':'',
                     'ap':'',
                     'sta_tag':'',
                     'dot1': False,
                     'active_ap_tag':'',#@author: yuyanan @since: 2014-7-30 optimize :get ap_mac via ap_tag
                     }
        self.conf.update(conf)
            
        if self.conf.has_key('zd'):
            self.zd=self.carrierbag[self.conf['zd']]
        else:
           self.zd = self.testbed.components['ZoneDirector']            
        if self.conf['user']:
            self.user = [self.conf['user']]
        else:
            self.user = []    
        self.wlan = self.conf['wlan']
        #@author: yuyanan @since: 2014-7-30 optimize :get ap_mac via ap_tag
        #if self.conf['active_ap_tag']:
        #    ap_mac = tconfig.get_active_ap_mac(self.testbed,self.conf['active_ap_tag'])
        #    self.ap = ap_mac
        #else:    
        #    self.ap = self.conf['ap']
        logging.info("check alarm in zd %s"%self.zd.ip_addr)


    def _get_expect_msg(self):
        #MSG_client_del_by_admin={user} disconnected by admin from {wlan} at {ap}
        #User[ras.eap.user] disconnected by admin from WLAN[Radius_Enhancement_DM_Hotspot] at AP[58:93:96:2b:b1:40]

        message=self.zd.messages
        

        #If mac authentication is enabled,mac addresses will be used as the username   
        if self.conf['sta_tag'] and not self.conf['user']: 
            logging.info('Will use station mac as the username')       
            target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
            target_station_mac = target_station.get_wifi_addresses()[1]
             
            import itertools
            temp1 = target_station_mac.lower()#aa:bb:cc:dd:ee:ff
            temp = temp1.split(':')
            temp2 = "".join(itertools.chain(temp))#aabbccddeeff  
            self.user = [temp2,
                         temp1,
                         temp1.replace(':', '-'),
                         temp2.upper(),
                         temp1.upper(),
                         temp1.upper().replace(':', '-')]

        event_msg_list = []
        if self.conf['event'] in ['MSG_client_del_by_admin']:
            for user in self.user:
                event_msg =message[self.conf['event']]
                event_msg=event_msg.replace('{user}','User[%s]'%user)
                event_msg=event_msg.replace('{wlan}','WLAN[%s]'%self.wlan)
                #event_msg=event_msg.replace('{ap}','AP[%s]'%self.ap)
                event_msg=event_msg.split(' at ')[0]
                event_msg = str(event_msg)
                logging.info("expected msg is '%s'"%event_msg)
                event_msg_list.append(event_msg)
        return event_msg_list

