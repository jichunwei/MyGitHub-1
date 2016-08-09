import logging
import time
from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zdcli import station_info_cli as StaGetter

class CB_ZD_CLI_Verify_Station_Info(Test):
    
    def _init_params(self, conf):        
        self.conf = {'sta_tag':'',
                     'Authorized':'',
                     'vlan':''
                     }
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']    
        if self.conf.get('zdcli_tag'):
            self.zdcli=self.carrierbag[self.conf['zdcli_tag']]                    
        logging.info("====Initialize Params DONE====")
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            sta_wifi_mac_addr = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
        except:
            target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
            sta_wifi_ip_addr, sta_wifi_mac_addr = target_station.get_wifi_addresses()
        
        res, msg = self.verify_station_info(sta_wifi_mac_addr)
        return self.returnResult(res, msg)
    
    def cleanup(self):
        self._update_carribag()

    def verify_station_info(self,sta_wifi_mac_addr):
        timeout = 240
        s_t = time.time()
        client_data = {}
        found = False
        while time.time() - s_t < timeout:
                
            client_data = StaGetter.show_current_active_client_by_mac(self.zdcli,sta_wifi_mac_addr.lower())
            if not client_data:
                client_data = StaGetter.show_current_active_client_by_mac(self.zdcli,sta_wifi_mac_addr.upper())
            if not client_data:
                found = False
                logging.warning('Not any clients found, re-check.')
                
            elif client_data:
                found = True
                res = self._verify_station_info(client_data)
                if res:
                    return('PASS','Station info is the same as expected!')
            time.sleep(5)           
        if not found:
            return('FAIL','No information about station[%s] is found.'%sta_wifi_mac_addr)
        else:
            return ('FAIL', "Station[%s] if found, but info is not expected!"%sta_wifi_mac_addr)
    def _verify_station_info(self,client_data):
        """
        {'Access Point': '24:c9:a1:19:c5:e0',
         'Auth Method': 'OPEN',
         'BSSID': '24:c9:a1:19:c5:e8',
         'Channel': '8',
         'Connect Since': '2014/12/22 16:25:05',
         'Host Name': 'lab-STA1',
         'Mac Address': '2c:d0:5a:0d:13:f8',
         'OS/Type': 'Windows 7/Vista',
         'Radio': '802.11gn',
         'Received from client': '394 pkts / 61890 bytes',
         'Role': '',
         'Signal': '70',
         'Status': 'Authorized',
         'Transmitted to client': '530 pkts / 40563 bytes',
         'Tx. drops due to retry failure': '7 pkts',
         'User/IP': '192.168.0.107',
         'User/IPv6': '',
         'VLAN': '20',
         'WLAN': 'atb160opennone'}
        """
        errmsg = ''
        expect_status = ''
        if self.conf.get('Authorized'):
            if self.conf('Authorized'):
                expect_status = 'Authorized'
            else:
                expect_status = 'Unauthorized'
        if expect_status and expect_status != client_data['Status']:
            errmsg += 'Status inconsistent, expected %s, actual %s.' %(expect_status, client_data['Status'])
        if self.conf.get('vlan'):
            expect_vlan = self.conf['vlan']
            if type(expect_vlan) != type([]):
                expect_vlan = [str(expect_vlan)]
            if not client_data['VLAN'] in expect_vlan:
                errmsg += 'Status inconsistent, vlan %s is not in expect list %s.' %(client_data['VLAN'],expect_vlan)
                
        if errmsg:
            logging.info(errmsg)
            return False
        else:
            return True
                
            