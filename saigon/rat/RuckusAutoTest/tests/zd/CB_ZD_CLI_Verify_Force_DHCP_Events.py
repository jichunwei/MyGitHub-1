"""
   Description: 
   @author: Jane Guo
   @contact: guo.can@odc-ruckuswireless.com
   @since: May 2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:
        - 'ap_mac': mac of AP,
        - 'wlan_cfg': wlan cfg,
        - 'dhcp_lease_time' : 120,
        - 'event_type': 'timeout,block'}
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Get events from CLI
        - Check event        
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Check Force DHCP events on ZD CLI success
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_CLI_Verify_Force_DHCP_Events(Test):
    required_components = ['ZoneDirector','ZoneDirectorCLI']
    parameters_description = {'ap_mac': '',
                 'wlan_cfg': {},
                 'dhcp_lease_time' : 120,
                 'event_type': 'timeout'}
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        self._retrieve_carribag()
        
    def test(self):
        try:
            logging.info("Check Force DHCP events on ZD CLI")
            self._check_force_dhcp_events()
                
        except Exception, ex:
            self.errmsg = 'Check Force DHCP events on ZD CLI failed:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:
            self._update_carrier_bag()
            pass_msg = 'Check Force DHCP events on ZD CLI success'
            return self.returnResult('PASS', pass_msg)
        
    def cleanup(self):
        pass
        
    def _cfg_init_test_params(self, conf):
        self.conf = {'ap_mac': '',
                 'wlan_cfg': {},
                 'dhcp_lease_time' : 120,
                 'event_type': 'timeout'}
        self.conf.update(conf)
        self.ap_mac = self.conf['ap_mac']     
        self.wlan_cfg = self.conf['wlan_cfg']
        self.dhcp_lease_time = self.conf['dhcp_lease_time']
        self.event_type = self.conf['event_type']
        self.event_name = self._get_event_name(self.event_type)
        
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']          
        self.errmsg = ''

    def _retrieve_carribag(self):
        self.sta_dhcp_ip = self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr']
        self.sta_dhcp_mac = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
        self.sta_ip = self.carrierbag[self.conf['sta_tag']]['wifi_ip_cfg']['addr']
                
    def _update_carrier_bag(self):
        pass

    def _get_event_name(self, event_type):
        if event_type == 'timeout':
            return "MSG_client_disconnect_force_dhcp_timeout"
        elif event_type == 'block':
            return "MSG_client_auth_fail_block"
        else:
            return ""
            
    def _check_force_dhcp_events(self):
        all_events = lib.zdcli.show._show_events_activities(self.zdcli)
        events = all_events['Last 300 Events/Activities']['Activity']
        cfg = self._init_check_message()
        try:
            for i in range(0,len(events)):
                if cfg['event_msg'] == events[i]['Activities']:
                    return
        except Exception, e:
            self.errmsg = 'Check force dhcp events from ZD CLI fail:%s' % (e.message)
        self.errmsg = "Can't find %s in events %s" % (cfg['event_msg'], events)
    
    def _init_check_message(self):
        """
        MSG_client_disconnect_force_dhcp_timeout=User{sta-mac} disassociated from {wlan} at {ap} due to force DHCP timeout. 
        User IP {sta-ip}, {vlan}, DHCP-assigned-IP {sta-dhcp-ip}, DHCP lease time {sta-dhcp-lease}.
        
        MSG_client_auth_fail_block={user} fails authentication too many times in a row when joining {wlan} at {ap}. {user} is temporarily blocked from the system for {block}.
        User[00:24:d7:96:86:18] fails authentication too many times in a row when joining WLAN[rat-force-dhcp] at AP[c0:8a:de:3b:f8:20]. User[00:24:d7:96:86:18] is temporarily blocked from the system for [30 seconds].
        """
        message=self.zd.messages
        event_msg =message[self.event_name]
        if self.event_name == "MSG_client_disconnect_force_dhcp_timeout":
            event_msg=event_msg.replace('{sta-mac}','[%s]' % self.sta_dhcp_mac.lower())
            event_msg=event_msg.replace('{wlan}','WLAN[%s]' % self.wlan_cfg['ssid'])
            event_msg=event_msg.replace('{ap}','AP[%s]' % self.ap_mac)
            event_msg=event_msg.replace('{sta-ip}','[%s]' % self.sta_ip)
            if self.wlan_cfg.has_key('vlan_id') and self.wlan_cfg['vlan_id']:
                event_msg=event_msg.replace('{vlan}','VLAN[%s]' % self.wlan_cfg['vlan_id'] ) 
            else:
                event_msg=event_msg.replace('{vlan}','VLAN[1]') 
            event_msg=event_msg.replace('{sta-dhcp-ip}','[%s]' % self.sta_dhcp_ip)
            event_msg=event_msg.replace('{sta-dhcp-lease}','[%s]' % self.dhcp_lease_time)
            return event_msg
        elif self.event_name == "MSG_client_auth_fail_block":
            event_msg=event_msg.replace('{user}','User[%s]' % self.sta_dhcp_mac.lower())
            event_msg=event_msg.replace('{wlan}','WLAN[%s]' % self.wlan_cfg['ssid'])
            event_msg=event_msg.replace('{ap}','AP[%s]' % self.ap_mac)
            event_msg=event_msg.replace('{block}','[30 seconds]')
            return event_msg