'''
Description:

This script is used to verify the WLANs' status and wlan group for active AP via ZD WebUI.

Created on 2012-11-25
@author: zoe.huang@ruckuswireless.com

'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import aps as apsobject

class CB_ZD_Verify_AP_WlanGroupInfo_WlanStatus_By_Macaddr(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyAPWlanGroupandStatus()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self.passmsg = "The stauts of all wlans to be verified for AP[%s} and wlan group info is correct via ZD WebUI" % self.ap_macaddr                 
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        '''
        conf: 
        {'ap_tag': '',
          'wlan_group':{'na':'Default',
                        'ng':'Default' or 'bg': 'Default'}
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
        self.zd = self.testbed.components['ZoneDirector']
        self.ap_tag = self.conf['ap_tag']
        self.active_ap = self.carrierbag[self.ap_tag]['ap_ins']
        self.ap_macaddr = self.active_ap.base_mac_addr
        self.wlan_group = self.conf.get('wlan_group', {})
        self.upwlanlist = self.conf.get('up', {})
        self.downwlanlist = self.conf.get('down', {})
        
        self.errmsg = ''
        self.passmsg = ''

    def _verifyAPWlanGroupandStatus(self):
        logging.info('Verify wlan group info and wlan status for AP[%s]' % self.ap_macaddr)
        try:
            #Check wlan group
            if len(self.wlan_group) != 0:
                logging.info('Begin to check wlan group info for AP[%s]' % self.ap_macaddr)
                for (radio,group) in self.wlan_group.iteritems():
                    ap_detail = apsobject.get_ap_detail_under_radio_by_mac_addr(self.zd, self.ap_macaddr, radio)
                    if len(ap_detail)==0:
                        self.errmsg += 'Get detail info for radio:%s failed' % radio
                        logging.info('Get detail info for radio:%s failed' % radio)
                    else:
                        if ap_detail['wlangroup'] != group:
                           self.errmsg += 'Get wlan group under radio:%s from webUI is %s, expected %s' % \
                           (radio,ap_detail['wlangroup'],group) 
            else:
                 logging.info("No need to check wlan group for AP")    
            #group wlan by radio and status
            logging.info('Get wlan list for AP[%s] from ZD WebUI' % self.ap_macaddr)
            wlan_info = apsobject.get_ap_detail_wlan_list_by_mac_addr(self.zd, self.ap_macaddr)
            '''
            [{u'bssid': u'04:4f:aa:07:50:08',
             u'radio_type': u'802.11g/n',
             u'vap_up': u'Up',
             u'wlan': u'ZoeWlan1'},
            {u'bssid': u'04:4f:aa:47:50:08',
             u'radio_type': u'802.11g/n',
             u'vap_up': u'Up',
             u'wlan': u'Wlan2'}]
            '''
            if len(self.upwlanlist) == 0 and len(self.downwlanlist) == 0:#no wlan should be listed in WLAN table
                if len(wlan_info) != 0:
                    self.errmsg += 'There should be no wlans listed in WLAN table, but wlans[%s] exist. Error!' % wlan_info
                else:
                    logging.info('UPWlanlist and Downwlanlist are both NULL, Wlan list got in WLAN table via ZD WebUI is also NULL. It is OK')
                return 
            
            wlans_24g_up = []
            wlans_24g_down = []
            wlans_5g_down = []
            wlans_5g_up = []
            for wlan in wlan_info:
                if str(wlan['vap_up']).lower() == 'up':
                    #chen.tao @ 2014-02-17, to fix ZF-7224
                    if str(wlan.get('radio_type')).lower() == '802.11a/n' or str(wlan.get('radio_type_alias')).lower() == '802.11a/n': #5g
                        wlans_5g_up.append(str(wlan['wlan']))
                    else:#2.4g                      
                        wlans_24g_up.append(str(wlan['wlan']))
                        
                if str(wlan['vap_up']).lower() == 'down':
                    #chen.tao @ 2014-02-17, to fix ZF-7224
                    if str(wlan.get('radio_type')).lower() == '802.11a/n' or str(wlan.get('radio_type_alias')).lower() == '802.11a/n': #5g
                        wlans_5g_down.append(str(wlan['wlan']))
                    else:#2.4g                       
                        wlans_24g_down.append(str(wlan['wlan']))
        
            if len(self.upwlanlist) != 0:
                logging.info('Begin to check wlans: %s, the status of them should be up and listed in WLAN table' % self.upwlanlist)
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
                logging.info('Begin to check wlans: %s, the status of them should be down and listed in WLAN table' % self.downwlanlist)
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
        