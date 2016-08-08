# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module doc string is accurate since it will be used in report generation.

"""Description:

    Prerequisite (Assumptions about the state of the testbed/DUT):

    Required components:
    Test parameters:
    Result type: PASS/FAIL
    Results: PASS
             FAIL otherwise

    Messages:
        - If PASS,
        - If FAIL, prints out the reason for failure

    Test procedure:
    1. Config:
        -
    2. Test:
        -
    3. Cleanup:
        -

    How is it tested: (to be completed by test code developer)

"""


from RuckusAutoTest.models import Test


class CB_ZD_Verify_Station_In_Tunnel_Mode(Test):
    '''
    verify the station traffic in tunnel mode
    '''
    required_components = ['ZoneDirector', 'Station']
    parameter_description = {'target_station': '', 'sta_wifi_mac_addr': ''}
    
    
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
       
        
    def test(self):
        val1, msg = self._verify_station_in_tunnel_mode()
        if not val1:
            self.errmsg = msg
            return self.returnResult('FAIL', self.errmsg)
        
        if self.wlan_cfg['do_tunnel'] and not msg:
            self.passmsg = msg
            return self.returnResult('PASS', self.passmsg)
        elif self.wlan_cfg['do_tunnel'] and ("different to the ZD's port" in msg):
            self.errmsg = msg
            return self.returnResult('FAIL', self.errmsg)
        elif self.wlan_cfg['do_tunnel'] and ("the same as the AP's port" in msg):
            self.errmsg = msg
            return self.returnResult('FAIL', self.errmsg)
        
        elif self.wlan_cfg['do_tunnel'] == False and not msg:
            self.passmsg = msg
            return self.returnResult('PASS', self.passmsg)
        elif self.wlan_cfg['do_tunnel'] == False and ("different to the AP's port" in msg):
            self.errmsg = msg
            return self.returnResult('FAIL', self.errmsg)
        elif self.wlan_cfg['do_tunnel'] == False and ("the same as the ZD's port" in msg):
            self.errmsg = msg
            return self.returnResult('FAIL', self.errmsg)
        
        
    def cleanup(self):
        pass
    
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.wlan_cfg = self.conf['wlan_cfg']
        if self.conf['wlan_cfg'].has_key('do_tunnel') and self.conf['wlan_cfg']['do_tunnel'] == None:
            self.conf['wlan_cfg']['do_tunnel'] = False
        
        if self.conf.get('ap_tag'):
            self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
            self.ap_mac = self.active_ap.get_base_mac().lower()
        
        else: 
            self.ap_mac = str(self.conf['active_ap_mac']).lower()
            
        if self.carrierbag.has_key(self.conf['sta_tag']):
            self.sta_mac = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
        else:
            raise Exception('Do not exit the station object in the carrierbag')
        
        self.errmsg = ''
        self.passmsg = ''
    
    
    def _retrive_carrier_bag(self):
        pass
    
    
    def _update_carrier_bag(self):
        pass
    
    
    def _verify_station_in_tunnel_mode(self):
        try:
            msg = self.testbed.verify_station_mac_in_tunnel_mode(self.ap_mac, self.sta_mac, self.wlan_cfg['do_tunnel'])
            return (1, msg)
        except Exception, e:
            return (0, e.message)
            
            