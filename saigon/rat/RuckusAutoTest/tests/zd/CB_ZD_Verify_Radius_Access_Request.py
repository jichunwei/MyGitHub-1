
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

class CB_ZD_Verify_Radius_Access_Request(Test):
    required_components = ['ZoneDirector']
    parameter_description = {}

    def config(self, conf):
        self.conf = {'user_type':'radius', 'auth_method': 'pap', 'client_ip_display': False, 'clear_log': True}
        self.conf.update(conf)

        self.zd     = self.testbed.components['ZoneDirector']
        self.server = self.testbed.components['LinuxServer']

        self.active_ap      = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']

        self.errmsg = ""
        self.passmsg = ""

    def test(self):
        # Retrieve log data from nohup.out file in /home/lab
        try:
            time.sleep(3)
            log_data = self.server.get_radius_server_log_detail(clear_log=self.conf['clear_log'])
            logging.info(log_data)
        except Exception, e:
            return self.returnResult('FAIL', e.message)
        
        #Message type--> rad_recv: Access-Request packet from host 192.168.0.2:56881, id=0, length=205
        res = re.search(r'\s*rad_recv: Access-Request\s*', log_data)
        if not res:
            self.errmsg += "rad_recv: Access-Request not found, "

        # MAC format user name and password in Radius PAP auth-method
        sta_mac = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr'] #'00:25:9c:0f:3d:c1' format

        if self.conf['user_type'].lower() == 'mac-lower':
            mac_passphrase = sta_mac.replace(':', '')
        elif self.conf['user_type'].lower() == 'mac-upper-connecter':
            mac_passphrase = sta_mac.upper().replace(':', '-')
        else:
            mac_passphrase = ''

        #User-Name = "00-25-9C-0F-3D-C1"/"00259c0f3dc1"
        if self.conf['user_type'].lower() == 'radius':
            user_name = self.conf['user_name']
        else:
            user_name = mac_passphrase

        res = re.search(r'User-Name\s*=\s*"%s"\s*' % user_name, log_data)
        if not res:
            self.errmsg += "User-Name(%s) not found, " % user_name

        #Password for PAP auth-method: User-Password = "00-25-9C-0F-3D-C1"/"xxxx"
        if self.conf['auth_method'].lower() == 'pap':
            if (self.conf['user_type'].lower() == 'radius') or \
                (self.conf['password'] is not None and self.conf['password'] != ''):
                password = self.conf['password']
            else:
                password = mac_passphrase

            res = re.search(r'User-Password\s*=\s*"%s"\s*' % password, log_data)
            if not res:
                self.errmsg += "User-Password(%s) not found, " % password

        #Framed-IP-Address = 192.168.0.139
        if self.conf['client_ip_display'] and self.carrierbag[self.conf['sta_tag']].has_key('wifi_ip_addr'):
            sta_ip = self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr']

            res = re.search(r'Framed-IP-Address\s*=\s*%s\s*' % sta_ip, log_data)
            if not res:
                self.errmsg += "Framed-IP-Address(%s) not found" % sta_ip

        #Calling-Station-Id = "00-25-9C-0F-3D-C1"
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
        called_sta_id = bssid.upper().replace(':', '-')+':'+self.conf['wlan_cfg']['ssid']
        res = re.search(r'Called-Station-Id\s*=\s*"%s"\s*' % called_sta_id, log_data)
        if not res:
            self.errmsg += "Called-Station-Id(%s) not found, " % called_sta_id

        #NAS-Identifier = "AC-67-06-33-76-B8"
        nas_id = bssid.upper().replace(':','-')
        res = re.search(r'NAS-Identifier\s*=\s*"%s"\s*' % nas_id, log_data)
        if not res:
            self.errmsg += "NAS-Identifier(%s) not found, " % nas_id

        #Authentication result of access request: Sending Access-Accept of id 0 to 192.168.0.2 port 56881
        auth_result = self.conf['auth_result']
        res = re.search(r'\s*Sending *%s\s*' % auth_result, log_data)
        if not res:
            self.errmsg += "[Sending %s] not found, " % auth_result

        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)

        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
