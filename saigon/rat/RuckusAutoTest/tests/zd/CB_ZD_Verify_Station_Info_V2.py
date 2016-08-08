# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Chris Wang
   @contact: chris.wang@ruckuswireless.com
   @since: Aug 2011

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters:
        - chk_empty: Whether checking no information shown in ZD, values is True/False
        - check_status_timeout: Timeout for checking status
        - radio_mode: Radio mode of station
        - status: Expected client status in ZD, authorized, unauthorized
        - chk_radio: Whether checking radio mode, True/False
        - sta_tag: Station tag, and will get station instance and information from carrier bag based on sta_tag
        - ap_tag: Active Point tag, and will get active point instance and information from carrier bag based on ap_tag
        - username: User name of station login to wlan
        
   Test procedure:
    1. Config:
        - initilize test parameters, and get ZD component.         
    2. Test:
        - Verify client information in ZD is same as expected.  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If client information [status, ap mac, wlan ssid, addr, User/IP] is same as expected 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.common import lib_Constant as const

class CB_ZD_Verify_Station_Info_V2(Test):
    required_components = ['ZoneDirector']
    parameter_description = {'chk_empty': 'Whether checking no information shown in ZD, values is True/False',
                             'check_status_timeout':'Timeout for checking status',
                             'radio_mode': 'Radio mode of station',
                             'status': 'Expected client status in ZD, authorized, unauthorized',
                             'chk_radio':'Whether checking radio mode, True/False',
                             'sta_tag':'Station tag, and will get station instance and information from carrier bag based on sta_tag',
                             'ap_tag':'Active Point tag, and will get active point instance and information from carrier bag based on ap_tag',
                             'username' : 'User name of station login to wlan',
                             }

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._testVerifyStationInfoOnZD()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        self._updateCarrierBag()
        self.passmsg = 'Verify station information [%s] on zd successfully' % self.client_info_on_zd
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        #add by cwang#20110421, chk_empty parameter which is used for checking target station isn't shown.
        self.conf = {'check_status_timeout':120,
                     'username':'',
                     'chk_empty':False,
                     'radio_mode':None,
                     'status':'Authorized',
                     'chk_radio':True,
                     'sta_tag':'sta_1',
                     'ap_tag':'tap',
                     }

        self.conf.update(conf)
        self.wlan_cfg = conf['wlan_cfg']
        self.radio_mode = self.conf['radio_mode']
        if 'active_zd' in self.carrierbag:
            self.zd = self.carrierbag['active_zd']
        else:
            self.zd = self.testbed.components['ZoneDirector']
        self._retrieve_carribag()
        self.errmsg = ''
        self.passmsg = ''

    def _retrieve_carribag(self):
        try:
            self.sta_wifi_mac_addr = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
        except:
            if self.carrierbag.has_key('sta_wifi_mac_addr'):
                self.sta_wifi_mac_addr = self.carrierbag['sta_wifi_mac_addr']
            else:
                self.sta_wifi_mac_addr = None

        try:    
            self.sta_wifi_ip_addr = self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr']
        except:
            if self.carrierbag.has_key('sta_wifi_ip_addr'):
                self.sta_wifi_ip_addr = self.carrierbag['sta_wifi_ip_addr']
            else:
                self.sta_wifi_ip_addr = None
            
        #Get station ipv6 address if have.
        try:    
            self.sta_wifi_ipv6_addr_list = self.carrierbag[self.conf['sta_tag']]['wifi_ipv6_addr_list']
        except:
            if self.carrierbag.has_key('sta_wifi_ipv6_addr_list'):
                self.sta_wifi_ipv6_addr_list = self.carrierbag['sta_wifi_ipv6_addr_list']
            else:
                res, self.sta_wifi_ip_addr, self.sta_wifi_ipv6_addr_list, self.sta_wifi_mac_addr, errmsg = \
                            tmethod.renew_wifi_ip_address_ipv6(self.carrierbag.get(self.conf['sta_tag'])['sta_ins'], 
                                                               const.DUAL_STACK, 
                                                               30)
        
                
        try:    
            self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        except:
            if self.carrierbag.get('active_ap'):
                self.active_ap = self.carrierbag['active_ap'].values()[0]
            else:
                self.active_ap = None #@author: yuyanan @since: 2014-10-20 zf-8842

    def _testVerifyStationInfoOnZD(self):
        logging.info("Verify information of the target station shown on the Zone Director")
        if self.radio_mode in ['g', 'bg'] or self.wlan_cfg['encryption'].upper() in ['TKIP', 'WEP-64', 'WEP-128', 'WEP64', 'WEP128']:
            expected_radio_mode = ['802.11b/g', '802.11a']
        elif self.wlan_cfg['encryption'].upper() == 'AUTO' and \
             self.wlan_cfg.has_key('sta_encryption') and \
             self.wlan_cfg['sta_encryption'].upper() in ['TKIP', 'WEP-64', 'WEP-128', 'WEP64', 'WEP128']:
            expected_radio_mode = ['802.11b/g', '802.11a']
        else:
            expected_radio_mode = ['802.11ng', '802.11g/n', '802.11a/n', '802.11an']

        expected_ip = []
        expected_ip.append(self.sta_wifi_ip_addr)
        if self.sta_wifi_ipv6_addr_list:
            for wifi_ipv6_addr in self.sta_wifi_ipv6_addr_list:
                expected_ip.append(wifi_ipv6_addr)
                expected_ip.append('%s/%s' % (self.sta_wifi_ip_addr, wifi_ipv6_addr))
            
        if self.conf['status'].lower() == 'authorized':
            if self.wlan_cfg.get('auth')== 'mac' or (self.wlan_cfg.get('type') == 'hotspot' and self.conf.get('username') == 'mac.bypass'):
                import itertools
                mac_addr = self.sta_wifi_mac_addr.split(':')
                mac_address = "".join(itertools.chain(mac_addr))
                if not self.wlan_cfg.get('mac_addr_format'):
                    username = mac_address.lower()
                elif self.wlan_cfg.get('mac_addr_format') == 'aabbccddeeff':
                    username = mac_address.lower()
                elif self.wlan_cfg.get('mac_addr_format') == 'AABBCCDDEEFF':
                    username = mac_address.upper()
                elif self.wlan_cfg.get('mac_addr_format') == 'aa:bb:cc:dd:ee:ff':
                    username = self.sta_wifi_mac_addr.lower()
                elif self.wlan_cfg.get('mac_addr_format') == 'AA:BB:CC:DD:EE:FF':
                    username = self.sta_wifi_mac_addr.upper()
                elif self.wlan_cfg.get('mac_addr_format') == 'aa-bb-cc-dd-ee-ff':
                    username = self.sta_wifi_mac_addr.lower().replace(':', '-')
                elif self.wlan_cfg.get('mac_addr_format') == 'AA-BB-CC-DD-EE-FF':
                    username = self.sta_wifi_mac_addr.upper().replace(':', '-')
                
            elif self.wlan_cfg.get('type') in ['guest', 'guest-access']:
                if self.conf.get('use_guestpass_auth'):
                    username = self.conf['guest_name']
                else:
                    username = 'guest'
            elif self.wlan_cfg.get('auth') == 'EAP':
                username = self.wlan_cfg['username']
            elif self.wlan_cfg.get('web_auth') or self.wlan_cfg.get('do_webauth'):
                username = self.conf.get('username')
            elif self.wlan_cfg.get('type') == 'hotspot':
                username = self.conf['username']
            else:
                username = None

            if username:
                for index,item in enumerate(expected_ip):
                    expected_ip[index] = username + '/' + item
                expected_ip.append(username)
        #********************************************************
        try:
            exp_client_info = {"ip": expected_ip,
                               "status": self.conf['status'],
                               "wlan": self.wlan_cfg['ssid'],
                               "radio": expected_radio_mode,
                               "apmac": self.active_ap.base_mac_addr
                           }
        except:
            exp_client_info = {"ip": expected_ip,
                               "status": self.conf['status'],
                               "wlan": self.wlan_cfg['ssid'],
                               "radio": expected_radio_mode,
#                               "apmac": self.active_ap.base_mac_addr
                           }
        #@author:yuyanan @since:2014-8-6 zf-8842 add ap description process when ap description exist    
        if self.active_ap:
            ap_info = self.zd._get_ap_info(self.active_ap.base_mac_addr)
            ap_description = ap_info.get('description')
            if ap_description: 
                exp_client_info['apmac'] = ap_description
        
        #updated by cwang@20140216
        if self.conf.get('role'):
            exp_client_info['role'] = self.conf.get('role')

        #added by cwang, skip checking radio status.
        if not self.conf['chk_radio']:
            exp_client_info.pop('radio')

        self.errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.zd,
                                                                              self.sta_wifi_mac_addr,
                                                                              exp_client_info,
                                                                              self.conf['check_status_timeout'])
        
        logging.info('Client information in ZD is %s' % (self.client_info_on_zd))
        
        if 'chk_empty' in self.conf:
            if self.conf['chk_empty']:
                if self.errmsg and self.errmsg.find("Zone Director didn't show any information") >= 0:
                    self.errmsg = ''
                else:
                    self.errmsg = 'The client info should not be shown in zd'

    def _updateCarrierBag(self):
        self.carrierbag['client_info_on_zd'] = self.client_info_on_zd
