
"""
Description: To verify if ZD could send radius accounting message to radius accounting server correctly
            Including Acct-Start, Acct-Interm-Update, Acct-Stop.  
"""

import os
import time
import logging
import re
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Station
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.common import Ratutils as utils

class CB_ZD_Verify_Radius_Acct_Message(Test):
    required_components = ['ZoneDirector']
    parameter_description = {}

    def config(self, conf):
        self.conf = {'called_sta_id_type':'wlan-bssid', 'log_display': True, 'clear_log': True}
        self.conf.update(conf)

        self.zd     = self.testbed.components['ZoneDirector']
        self.server = self.testbed.components['LinuxServer']

        self.active_ap      = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']

        self.errmsg = ""
        self.passmsg = ""

    def test(self):
        #Wait until session time exceeds 
        if self.conf.get('acct_session_time'):
            time.sleep(self.conf['acct_session_time'])

        # Retrieve log data from nohup.out file in /home/lab
        try:
            log_data = self.server.get_radius_server_log_detail(clear_log=self.conf['clear_log'])
            logging.info(log_data)
        except Exception, e:
            return self.returnResult('FAIL', e.message)

        #Acct-Status-Type = Start/Stop/Interim-Update
        acct_status_type = self.conf['acct_status_type']
        res = re.search(r'Acct-Status-Type\s*=\s*%s\s*' % acct_status_type, log_data)
        if self.conf['log_display'] == True:
            if not res:
                self.errmsg += "Acct-Status-Type(%s) not found, " % acct_status_type
        else:
            if res:
                self.errmsg += "Acct-Status-Type(%s) was found, the message should not be generated at all!" % acct_status_type
                return self.returnResult('FAIL', self.errmsg)

            return self.returnResult('PASS', self.passmsg)

        #User-Name = "xxxxxx"
        acct_user_name = self.conf['acct_user_name']
        res = re.search(r'User-Name\s*=\s*"%s"\s*' % acct_user_name, log_data)
        if not res:
            self.errmsg += "User-Name(%s) not found, " % acct_user_name

        if acct_status_type == 'Start':
            self._verify_acct_start_msg(log_data)
        elif acct_status_type == 'Interim-Update':
            self._verify_acct_interim_update_msg(log_data)
        else:
            self._verify_acct_stop_msg(log_data)

        #Acct-Authentic = RADIUS
        acct_authentic = self.conf['acct_authentic']
        res = re.search(r'Acct-Authentic\s*=\s*%s\s*' % acct_authentic, log_data, re.I)
        if not res:
            self.errmsg += "Acct-Authentic(%s)  not found, " % acct_authentic

        #Framed-IP-Address = 192.168.0.139
        if self.carrierbag[self.conf['sta_tag']].has_key('wifi_ip_addr'):
            sta_ip = self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr']

            res = re.search(r'Framed-IP-Address\s*=\s*%s\s*' % sta_ip, log_data)
            if not res:
                self.errmsg += "Framed-IP-Address(%s) not found" % sta_ip

        #Calling-Station-Id = "00-25-9C-0F-3D-C1"
        if self.carrierbag[self.conf['sta_tag']].has_key('wifi_mac_addr'):
            sta_mac = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr'] #'00:25:9c:0f:3d:c1' format
            calling_sta_id = sta_mac.upper().replace(':', '-')
            res = re.search(r'Calling-Station-Id\s*=\s*"%s"\s*' % calling_sta_id, log_data)
            if not res:
                self.errmsg += "Calling-Station-Id(%s) not found, " % calling_sta_id

        #NAS-IP-Address = 192.168.0.2
        zd_cfg = self.zd.get_ip_cfg()
        res = re.search(r'NAS-IP-Address\s*=\s*%s\s*' % zd_cfg['ip_addr'], log_data)
        if not res:
            self.errmsg += "NAS-IP-Address(%s) not found, " % zd_cfg['ip_addr']

        #get WLAN BSSID of active AP
        bssid = self.active_ap.get_bssid_by_ssid(self.conf['wlan_cfg']['ssid'])
        if not bssid:
            self.errmsg += "BSSID is not found in AP CLI"

        #Called-Station-Id = "AC-67-06-33-76-B8:kevin-wisr-1981"
        if self.conf['called_sta_id_type'] == 'wlan-bssid':
            called_sta_id = bssid.upper().replace(':', '-')+':'+self.conf['wlan_cfg']['ssid']
        else:
            #'ap-mac'
            called_sta_id = self.active_ap.base_mac_addr.upper().replace(':', '-')+':'+self.conf['wlan_cfg']['ssid']
        res = re.search(r'Called-Station-Id\s*=\s*"%s"\s*' % called_sta_id, log_data)
        if not res:
            self.errmsg += "Called-Station-Id(%s) not found, " % called_sta_id

        #NAS-Identify = "xxxxxx"
        self._verify_acct_nas_id_type(log_data, bssid)

        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)

        return self.returnResult('PASS', self.passmsg)

    def _verify_acct_start_msg(self, data):
        pass

    def _verify_acct_interim_update_msg(self, data):
        acct_session_time = self.conf['acct_session_time']
        res = re.search(r'Acct-Session-Time\s*=\s*%s\s*' % acct_session_time, data)
        if not res:
            self.errmsg += "Acct-Session-Time(%s) not found, " % acct_session_time

    def _verify_acct_stop_msg(self, data):
        pass

    def _verify_acct_nas_id_type(self, data, bssid):
        nas_id = ''
        if self.conf['acct_nas_id_type'] == 'wlan-bssid':
            nas_id = bssid.upper().replace(':','-')
        elif self.conf['acct_nas_id_type'] == 'mac-addr':
            zd_mac = self.zd.mac_addr
            nas_id = zd_mac.upper().replace(':','-')
        else:
            nas_id = self.conf['user_define_string']

        res = re.search(r'NAS-Identifier\s*=\s*"%s"\s*' % nas_id, data)
        if not res:
            self.errmsg += "NAS-Identifier(%s) not found, " % nas_id

    def cleanup(self):
        pass
