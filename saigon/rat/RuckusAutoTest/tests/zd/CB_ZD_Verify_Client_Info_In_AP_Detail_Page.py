'''
by west
verify the client number in ap brief page is the sam with expected
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd.aps import get_ap_client_detail_by_mac
import libZD_TestConfig as tconfig

class CB_ZD_Verify_Client_Info_In_AP_Detail_Page(Test):
    '''
    '''

    def config(self, conf):
        '''
        '''
        self._cfg_init_test_params(conf)


    def test(self):
        '''
        '''
        info = get_ap_client_detail_by_mac(self.zd,self.ap_mac_addr,self.sta_mac)
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
            'ap_mac':'',
            'sta_tag':'',
            'info':{}
        }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        
        if self.conf.has_key('ap_tag') and self.conf['ap_tag']:
            active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['ap_tag'])
            self.ap_mac_addr = active_ap.base_mac_addr
        else:
            self.ap_mac_addr = self.conf['ap_mac']
        
        sta = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        self.sta_mac = sta.get_wifi_addresses()[1]
        
        self.conf['info'].update({'ap':self.ap_mac_addr})
        self.info=self.conf['info']
        
        self.errmsg = ""
        self.passmsg = "sta info verify successfully"
        