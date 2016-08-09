'''
by west
verify the client number in wlan detail page is the same with expected
'''
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd.wlan_zd import get_wlan_client_info_by_mac

class CB_ZD_Verify_Client_Info_In_Wlan_Detail_Page(Test):
    '''
    '''

    def config(self, conf):
        '''
        '''
        self._cfg_init_test_params(conf)


    def test(self):
        '''
        '''
        info = get_wlan_client_info_by_mac(self.zd,self.wlan,self.sta_mac)
        for key in self.info:
            if self.info[key].lower()!=info[key].lower():
                self.errmsg+='%s not match:%s instead of %s'%(key,info[key],self.info[key])

        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)

        logging.debug(self.passmsg)
        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        '''
        '''


    def _cfg_init_test_params(self, conf):
        '''
        info=
        {'action': '',
         'ap': '50:a7:33:2e:42:e0',
         'auth_method': 'OPEN',
         'channel': '4',
         'dvcinfo': 'Windows XP',
         'hostname': 'tb3-sta2',
         'mac': '00:15:af:ed:94:3b',
         'radio_type': '802.11g/n',
         'rssi': '99%',
         'status': 'Authorized',
         'user': '192.168.0.147',
         'vlan': '1',
         'wlan': 'new_wlan_19811'}
        '''
        self.conf = {
            'wlan_name':'',
            'sta_tag':'',
            'info':{}
        }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.wlan = self.conf['wlan_name']
        sta = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        self.sta_mac = sta.get_wifi_addresses()[1]
        self.info=self.conf['info']
        
        self.errmsg = ""
        self.passmsg = "sta info verify successfully"
        