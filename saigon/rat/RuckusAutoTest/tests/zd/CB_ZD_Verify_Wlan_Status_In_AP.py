'''
Description:

This script is used to verify the WLANs' status in the active AP.

Created on 2012-11-25
@author: zoe.huang@ruckuswireless.com

'''

import logging
import time

from RuckusAutoTest.models import Test


class CB_ZD_Verify_Wlan_Status_In_AP(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyWlanStautsInAP()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self.passmsg = "The stauts of all wlans to be verified are correct in the active AP"                  
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        '''
        conf: 
        {'ap_tag': '',
          'up':{'24g': [openwlan1,openwlan2], # ssid list
                '5g':[openwlan7,openwlan8]}
          },
          'down':{'24g':[openwlan3,openwlan4],
                  '5g':[openwlan9,openwlan10]
          }
        }

        '''
        self.conf = {}                        
        self.conf.update(conf)
        self.ap_tag = self.conf['ap_tag']
        self.active_ap = self.carrierbag[self.ap_tag]['ap_ins']
        
        self.upwlanlist = self.conf.get('up', {})
        self.downwlanlist = self.conf.get('down', {})
        
        self.errmsg = ''
        self.passmsg = ''

    def _verifyWlanStautsInAP(self):
        logging.info('Verify wlan status in active AP[%s]' % self.active_ap.get_base_mac())
        try:
            time.sleep(15)#wait for the status change
            wlan_info = self.active_ap.get_info_for_external_wlans()
            logging.info('All wlan info in AP is: %s' % wlan_info)
            
            if len(self.upwlanlist) == 0 and len(self.downwlanlist) == 0:#no wlan should be on AP
                if len(wlan_info) != 0:
                    self.errmsg += 'There should be no wlans in AP, but wlans[%s] exist. Error!' % wlan_info
                else:
                    logging.info('UPWlanlist and Downwlanlist are both NULL, External wlan list got in AP CLI is also NULL. It is OK')
                return            
            #group wlan by radio and status         
            wlans_24g_up = []
            wlans_24g_down = []
            wlans_5g_down = []
            wlans_5g_up = []
            for (wlanid, wlan) in wlan_info.iteritems():
                if wlan['status'].lower() == 'up' and wlan['bssid'] != '00:00:00:00:00:00':
                    if wlan['radioID'] == '0': #2.4g
                        wlans_24g_up.append(wlan['ssid'])
                    else:#5g                      
                        wlans_5g_up.append(wlan['ssid'])
                        
                if wlan['status'].lower() == 'down':
                    if wlan['radioID'] == '0': #2.4g
                        wlans_24g_down.append(wlan['ssid'])
                    else:#5g                      
                        wlans_5g_down.append(wlan['ssid'])
        
            
            if len(self.upwlanlist) != 0:
                logging.info('Begin to check wlans: %s, the status of them should be up' % self.upwlanlist)
                if self.upwlanlist.has_key('24g'):
                    expected_24g_wlan = self.upwlanlist['24g']
                    logging.info('Check wlans under 2.4g: %s, the status of them should be up' % expected_24g_wlan)                   
                    if len(expected_24g_wlan) != len(wlans_24g_up):
                        self.errmsg += 'Wlans[%s] under 2.4g should be up, but they are not all up, up wlans[%s]' % (expected_24g_wlan, wlans_24g_up)
                    else:
                        for wlanssid in expected_24g_wlan:
                            if wlanssid not in wlans_24g_up:
                                self.errmsg += 'Wlan[%s] under 2.4g should be up, but it is not' % (wlanssid) 
                                logging.info('Wlan[%s] under 2.4g should be up, but it is not' % (wlanssid))
                            
                if self.upwlanlist.has_key('5g'):
                    expected_5g_wlan = self.upwlanlist['5g']
                    logging.info('Check wlans under 5g: %s, the status of them should be up' % expected_5g_wlan)
                    if len(expected_5g_wlan) != len(wlans_5g_up):
                        self.errmsg += 'Wlans[%s] under 5g should be up, but they are not all up, up wlans[%s]' % (expected_5g_wlan, wlans_5g_up)
                    else:
                        for wlanssid in expected_5g_wlan:
                            if wlanssid not in wlans_5g_up:
                                self.errmsg += 'Wlan[%s] under 5g should be up, but it is not' % (wlanssid) 
                                logging.info('Wlan[%s] under 5g should be up, but it is not' % (wlanssid))
            else:
                # the status of all wlans should be down
                if (len(wlans_24g_down)+ len(wlans_5g_down))!= len(wlan_info):
                    self.errmsg += 'UpWlanlist is NULL, all wlans should be down, but it is not' 
                    logging.info('UpWlanlist is NULL, all wlans should be down, but it is not')
                            
            if len(self.downwlanlist) != 0:
                logging.info('Begin to check wlans: %s, the status of them should be down' % self.downwlanlist)
                if self.downwlanlist.has_key('24g'):
                    expected_24g_wlan = self.downwlanlist['24g']
                    logging.info('Check wlans under 2.4g: %s, the status of them should be down' % expected_24g_wlan)
                    if len(expected_24g_wlan) != len(wlans_24g_down):
                        self.errmsg += 'Wlans[%s] under 2.4g should be down, but they are not all down, down wlans[%s]' % (expected_24g_wlan, wlans_24g_down)
                    else:
                        for wlanssid in expected_24g_wlan:
                            if wlanssid not in wlans_24g_down:
                                self.errmsg += 'Wlan[%s] under 2.4g should be down, but it is not' % (wlanssid) 
                                logging.info('Wlan[%s] under 2.4g should be down, but it is not' % (wlanssid))
                            
                if self.downwlanlist.has_key('5g'):
                    expected_5g_wlan = self.downwlanlist['5g']
                    logging.info('Check wlans under 5g: %s, the status of them should be down' % expected_5g_wlan)
                    if len(expected_5g_wlan) != len(wlans_5g_down):
                        self.errmsg += 'Wlans[%s] under 5g should be down, but they are not all down, down wlans[%s]' % (expected_5g_wlan, wlans_5g_down)
                    else:
                        for wlanssid in expected_5g_wlan:
                            if wlanssid not in wlans_5g_down:
                                self.errmsg += 'Wlan[%s] under 5g should be down, but it is not' % (wlanssid) 
                                logging.info('Wlan[%s] under 5g should be down, but it is not' % (wlanssid))
            else:
              # the status of all wlans should be up
                if (len(wlans_24g_up)+ len(wlans_5g_up))!= len(wlan_info):
                    self.errmsg += 'DownWlanlist is NULL, all wlans should be up, but it is not' 
                    logging.info('DownWlanlist is NULL, all wlans should be up, but it is not')                   
                                            
        except Exception, ex:
            self.errmsg = ex.message
        