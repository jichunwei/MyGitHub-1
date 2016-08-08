'''
Description:
Created on 2010-7-8
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.components.lib.zd import user

class CB_ZD_SR_Web_Portal_Client_Status_Sync_Testing(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        self._test_client_status_sync()
        if self.errmsg:
            return ("FAIL", self.errmsg)
        
        self.passmsg = 'Web Portal client status can be synchronized to standby ZD'
        passmsg.append(self.passmsg)
        self._update_carrier_bag()
        
        return ["PASS", passmsg]
    
    
    def cleanup(self):
        pass
    
    
    def _retrive_carrier_bag(self):
        self.active_zd = self.carrierbag['active_zd']
        self.standby_zd = self.carrierbag['standby_zd']
        self.target_station = self.carrierbag['station']       
 
    
    def _update_carrier_bag(self):
        pass
  
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.check_status_timeout = 100
        self.errmsg = ''
        self.passmsg = ''
 

    def _refresh_standby_zd(self):
        try:
            self.standby_zd.refresh()
        except:
            pass  
        
            
    def _create_user(self):
        u_cfg = {'username':'ras.local.user',
                 'password':'ras.local.user',
                 'confirm_password':'ras.local.user',
                 }
        self.username = u_cfg['username']
        self.password = u_cfg['password']
        
        try:
            user.delete_user(self.active_zd, self.username)
        except:
            pass
        
        user.create_user(self.active_zd, u_cfg)
        return u_cfg
 
    
    def _create_wlan(self):
        w_cfg = {'ssid': 'rat-open-none-web-auth',
                 'description': 'EnjoyPythonscripting_Open',
                 'auth': 'open',
                 'use_web_auth': True,
                 'wpa_ver': '',
                 'encryption': 'none',
                 'sta_auth': 'open',
                 'sta_encryption': 'none',
                 'sta_wpa_ver': '',
                 'key_index': '',
                 'key_string': '',
                 'ad_domain': '',
                 'ad_addr': '',
                 'ad_port': '',
                 'ras_addr': '',
                 'ras_port': '',
                 'username': 'ras.local.user',
                 'password': 'ras.local.user',
                 'ras_secret': ''
                 }
        self.active_zd.cfg_wlan(w_cfg)
        return w_cfg
    
    
    def _test_client_status_sync(self):
        u_cfg = self._create_user()
        w_cfg = self._create_wlan()
        res = self._assign_client_to_wlan(w_cfg)
        if not res:
            return False    
            
        self._cfg_station_perform_webauth()
        
        a_c_list = self.active_zd.get_active_client_list()
        if not self._verify_client_status_on_zd(a_c_list, w_cfg, chk_status=u'Authorized'):
            return False
        
        self._refresh_standby_zd()
        s_c_list = self.standby_zd.get_active_client_list()
        if not self._verify_client_status_between_zds(a_c_list, s_c_list):
            return False
        
        logging.info('Try to de-auth client from wlan [%s]' % w_cfg['ssid'])
        self.active_zd.remove_all_active_clients()        
        a_c_list = self.active_zd.get_active_client_list()
        if not self._verify_client_status_on_zd(a_c_list, w_cfg, chk_status=u'Unauthorized'):
            return False
        self._refresh_standby_zd()
        s_c_list = self.standby_zd.get_active_client_list()
        if not self._verify_client_status_between_zds(a_c_list, s_c_list):
            return False
        
        logging.info('Try to remove WLAN [%s] from ZD and Client' % w_cfg['ssid'])
        self.active_zd.remove_wlan(w_cfg)
        self.target_station.remove_all_wlan()
        start_time = time.time()
        found = False
        while time.time() - start_time < self.check_status_timeout:
            time.sleep(5)
            a_c_list = self.active_zd.get_active_client_list()            
            for a_c in a_c_list:
                if a_c['wlan'] == w_cfg['ssid']:
                    found = True
                    continue
                
            self._refresh_standby_zd()            
            s_c_list = self.standby_zd.get_active_client_list()
            if not self._verify_client_status_between_zds(a_c_list, s_c_list):
                return False
                        
            else:
                found = False
                
        if found :
            self.errmsg = 'After [%s] seconds, WLAN[%s] showing on ZD' % (self.check_status_timeout, w_cfg['ssid'])
            logging.warning(self.errmsg)
            return False
        
        self.passmsg = 'Current Active clients shown on ZD have synchronized to standby ZD correctly'
        logging.info(self.passmsg)
        
        return True
            

    def _cfg_station_perform_webauth(self):
        logging.info("Perform Web authentication on the target station %s" % self.target_station.get_ip_addr())

        arg = tconfig.get_web_auth_params(self.active_zd, self.username, self.password)
        self.target_station.perform_web_auth(arg)
        
            
    def _verify_client_status_on_zd(self, a_c_list, w_cfg, chk_status = u'Authorized'):
        fnd = False
        for a_c in a_c_list:            
            if a_c['wlan'] == w_cfg['ssid']:
                fnd = True
                if a_c['status'] != chk_status:
                    self.errmsg = 'WLAN [%s] has not been associated by Station [%s]' % (w_cfg['ssid'], w_cfg['mac'])
                    return False
                break
            
        if not fnd:
            self.errmsg = 'WLAN [%s] has not been found in active client list' % w_cfg['ssid']
            return False
    
    
    def _verify_client_status_between_zds(self, a_c_list, s_c_list):
        size = len(a_c_list)
        for i in range(size):
            a_c = a_c_list[i]
            s_c = s_c_list[i]
            if not self._verify_dict(a_c, s_c):
                return False
            
        self.passmsg = 'Current active client status has synchronized to standby ZD correctly'
        logging.info(self.passmsg)
        return True
                
                    
    def _assign_client_to_wlan(self, wlan_conf):
#        import pdb
#        pdb.set_trace()
        self.target_station.remove_all_wlan()
        time.sleep(10)
        errmsg = tmethod.assoc_station_with_ssid(self.target_station, wlan_conf, self.check_status_timeout)
        
        if errmsg:
            self.errmsg = '[Connect failed]: %s' % errmsg
            logging.info(self.errmsg)            
            return False
        
        return True
            

    def _verify_dict(self, target = dict(), source = dict()):
        for key, value in source.items():
            if target[key] != value :
                self.errmsg = 'Value can not match against key = %s' % key
                return False
        
        return True     
    
