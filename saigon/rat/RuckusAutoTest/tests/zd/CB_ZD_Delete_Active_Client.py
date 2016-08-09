'''
Description: This script is used to the station from the Zone Director's currently active clients.
Created on Jul 13, 2011
Author: Jacky Luh
Email: jluh@ruckuswireless.com
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig

class CB_ZD_Delete_Active_Client(Test):
    required_components = ['ZoneDirector', 'Station']
    parameter_description = {'target_station': '', 'sta_wifi_mac_addr': ''}
    

    def config(self, conf):
        self._initTestParameters(conf)


    def test(self):
        self._deleteStationOnZD()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)

        self.passmsg = "Delete the station from ZD's currently active clients successfully"

        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        pass


    def _initTestParameters(self, conf):
        self.conf = {'status': 'Authorized'}
        if conf.has_key('sta_tag') and conf['sta_tag']:
            self.conf.update(conf)
        else:
            raise Exception("The station obj no found.")
        
        self.sta_wifi_mac_addr = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
        self.sta_wifi_ip_addr = self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr']
        
        if self.conf['test_policy'] == 'guest access':
            if self.conf.has_key('use_guestpass_auth') and self.conf['use_guestpass_auth']:
                if self.conf.has_key('guest_name') and self.conf['guest_name']:
                    self.user_name = self.conf['guest_name']
            elif self.conf.has_key('use_guestpass_auth') and not self.conf['use_guestpass_auth']:
                self.user_name = 'guest'
            else:
                raise Exception("The guest_name no found.")
            
        elif self.conf['test_policy'] == 'web authentication':
            if self.conf.has_key('status') and self.conf['status'] == 'Authorized':
                self.user_name = self.conf['username']
            elif self.conf.has_key('status') and self.conf['status'] == 'Unauthorized':
                    self.user_name = self.sta_wifi_mac_addr
            else:
                raise Exception("The webauth_user no found.")
        
        elif self.conf['test_policy'] == 'hotspot authentication' and self.conf['username']:
            if self.conf.has_key('status') and self.conf['status'] == 'Authorized':
                self.user_name  = self.conf['username']
            elif self.conf.has_key('status') and self.conf['status'] == 'Unauthorized':
                self.user_name = self.sta_wifi_mac_addr
            else:
                raise Exception("The hotspot_user no found.")
            
        elif self.conf['test_policy'] == 'mac authentication':
            self.user_name = self.sta_wifi_mac_addr
            
        self.zd = self.testbed.components['ZoneDirector']

        self.errmsg = ''
        self.passmsg = ''
        
        
    def _retrive_carrier_bag(self):
        pass
    
    
    def _update_carrier_bag(self):
        pass
    

    def _deleteStationOnZD(self):
        # Clear all event before testing
        self.zd.clear_all_events()
        # Delete the client entry
        try:
            self.zd.delete_clients(self.sta_wifi_mac_addr)
        except Exception, e:
            self.errmsg = e.message
            
        # Verify the client deleted client events
        import time
        st = time.time()
        
        #MSG_client_del_by_admin={user} disconnected by admin from {wlan} at {ap}
        event = self.zd.messages['MSG_client_del_by_admin']
        event = event.replace('{user}', 'User[%s]' % self.user_name)
        event = event.replace('{wlan}', 'WLAN[%s]' % self.conf['wlan_cfg']['ssid'])
        event = event.replace('{ap}', '')
        exp_activity = event.lower()        
        
        while time.time() - st < 10:            
            time.sleep(2)
            self.all_events = self.zd.get_events()        
            for event in self.all_events:
                for item in event:
                    findevent = str(item).lower().find(exp_activity)
                    if findevent >= 0:
                        logging.info('The event "%s" is recorded on the Events table' % event)
                        return '' 
                    
                    
        logging.warning("Doesn't find event %s" % exp_activity)

