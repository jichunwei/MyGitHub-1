"""
   Description: 
   @author: Jane Guo
   @contact: guo.can@odc-ruckuswireless.com
   @since: May 2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:
        - 'wlan_cfg': 'wlan cfg'
        format: wlan_cfg = {"name" : "RAT-Open-Non-Force-DHCP",
                    "ssid" : "RAT-Open-Non-Force-DHCP",
                    "auth" : "open",
                    "encryption" : "none",
                    "force_dhcp" : True,
                    "force_dhcp_timeout" : 30
                    }
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Get the data from GUI
        - Get the data from CLI
        - Compare the data between GUI get and CLI get          
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If data are same between get and set 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.zdcli import get_wlan_info

class CB_ZD_Verify_Force_DHCP_GUI_CLI_Get(Test):
    required_components = ['ZoneDirector','ZoneDirectorCLI']
    parameters_description = {'wlan_cfg': {}}
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        try:
            ssid = self.wlan_cfg['ssid']
            logging.info("Get wlan info of ssid %s from GUI" % self.wlan_cfg['ssid'])
            
            gui_cfg = self._get_wlan_conf_detail(ssid)
            cli_cfg = self._get_cli_wlan_conf_detail(ssid)
            self._verify_force_dhcp_gui_cli_get(gui_cfg, cli_cfg)
                
        except Exception, ex:
            self.errmsg = 'Compare GUI get and CLI get failed:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:
            self._update_carrier_bag()
            pass_msg = 'GUI get and CLI get data are same'
            return self.returnResult('PASS', pass_msg)
        
    def cleanup(self):
        pass
        
    def _cfg_init_test_params(self, conf):
        self.conf = {'wlan_cfg': {}}
        self.conf.update(conf)       
        self.wlan_cfg = self.conf['wlan_cfg']
            
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
                  
        self.errmsg = ''
        
    def _update_carrier_bag(self):
        pass
    
    def _get_wlan_conf_detail(self, ssid):
        wlan_conf = lib.zd.wlan.get_wlan_conf_detail(self.zd, ssid)
        if not wlan_conf:
            self.errmsg = "Can't find wlan configuration on GUI"
        return wlan_conf
    
    def _get_cli_wlan_conf_detail(self, ssid):
        wlan_conf = get_wlan_info.get_wlan_by_ssid(self.zdcli, ssid)
        if not wlan_conf:
            self.errmsg = "Can't find wlan configuration on CLI"
        return wlan_conf

    def _verify_force_dhcp_gui_cli_get(self, gui_cfg, cli_cfg):
        #gui  'force_dhcp': 'Enabled' 'force_dhcp_timeout': u'30'
        #cli  'Force DHCP State': 'Enabled' 'Force DHCP Timeout': '30'
        logging.info("GUI config is %s" % gui_cfg)
        logging.info("CLI config is %s" % cli_cfg)       
        if gui_cfg.has_key('force_dhcp') and gui_cfg.has_key('force_dhcp_timeout'):
            if not gui_cfg['force_dhcp'] == cli_cfg['Force DHCP State']:
                self.errmsg = "Force dhcp between set and get is different"
            if not int(gui_cfg['force_dhcp_timeout']) == int(cli_cfg['Force DHCP Timeout']):
                self.errmsg = "Force dhcp timeout between set and get is different"
        else:
            self.errmsg = "Can't find force dhcp value in cfg"